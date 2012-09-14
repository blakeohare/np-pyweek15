from serverlib import poll
from serverlib import sql
from serverlib import util
from serverlib import settings


import random

def try_deplete_resources(user_id, food, water, aluminum, copper, silicon, oil):
	current = sql.query("SELECT * FROM `resource_status` WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	current = current[0]
	if current['food'] < food: return False
	if current['water'] < water: return False
	if current['aluminum'] < aluminum: return False
	if current['copper'] < copper: return False
	if current['oil'] < oil: return False
	
	sql.query("UPDATE `resource_status` SET " + ', '.join([
		"`food` = `food` - " + str(food),
		"`water` = `water` - " + str(water),
		"`aluminum` = `aluminum` - " + str(aluminum),
		"`copper` = `copper` - " + str(copper),
		"`silicon` = `silicon` - " + str(silicon),
		"`oil` = `oil` - " + str(oil)]) + " WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	return True

def do_build(user_id, client_token, last_id, sector, loc, type, poll_afterwards=True):
	sector = util.tsanitize(sector)
	loc = util.tsanitize(loc)
	last_id = util.parseInt(last_id)
	
	verify_position = sql.query("SELECT `hq_sector` FROM `user` WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	if verify_position[0]['hq_sector'] == sector:
		
		if client_token:
			duplicate = sql.query(
				'SELECT `client_token` FROM `event` WHERE `client_token` = %s', (client_token,))
			if not duplicate and validate_building(type, sector, loc):
				
				if try_deplete_resources(
					user_id,
					settings.building_cost[type][0],
					settings.building_cost[type][1],
					settings.building_cost[type][2],
					settings.building_cost[type][3],
					settings.building_cost[type][4],
					settings.building_cost[type][5]):
					
					data = 'Build:%s,%s' % (type, loc)
					event_id = sql.insert(
						'INSERT INTO `event` (`client_token`, `sector_xy`, `user_id`, `data`) VALUES (%s, %s, %s, %s)', (client_token, sector, user_id, data))
					quarry_data = ''
					if type == 'quarry':
						resources = 'a c s'.split(' ')
						distribution = [int(random.random() * 101)]
						rdist = int(random.random() * (100 - distribution[0] + 1))
						distribution.append(rdist)
						distribution.append(100 - sum(distribution))
						random.shuffle(distribution)
						
						quarry_data = 'a' + str(distribution[0]) + 'c' + str(distribution[1]) + 's' + str(distribution[2])
					sql.insert('INSERT INTO `structure` (`type`, `sector_xy`, `loc_xy`, `user_id`, `event_id`, `data`) VALUES (%s, %s, %s, %s, %s, %s)', (type, sector, loc, user_id, event_id, quarry_data))
				else:
					return { 'success': False, 'message': "Insufficient resources" }
			if poll_afterwards:
				return poll.do_poll(user_id, str(last_id) + '^' + sector)
		else:
			return { 'success':False, 'message': "missing client token" }
	else:
		return { 'success': False, 'message': "Cannot build this far from your HQ" }

def validate_building(type, sector, coordinate):
	#for now, having those is enough
	if type and sector and coordinate:
		x,y = map(int, coordinate.split('^'))
		others = sql.query("SELECT * FROM `structure` WHERE `sector_xy` = %s", (sector,))
		for other in others:
			ox,oy = map(int, other['loc_xy'].split('^'))
			otype = other['type']
			# TODO: make sure that x,y,type does not conflict geographically with ox,oy,otype
			# Buildings cannot be placed next to each other. 
		return True
	return False
