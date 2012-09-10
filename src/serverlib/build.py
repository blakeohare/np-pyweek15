from serverlib import poll
from serverlib import sql
from serverlib import util

def do_build(user_id, client_token, last_id, sector, loc, type, poll_afterwards=True):
	sector = util.tsanitize(sector)
	loc = util.tsanitize(loc)
	last_id = util.parseInt(last_id)
	if client_token:
		duplicate = sql.query(
			'SELECT `client_token` FROM `event` WHERE `client_token` = %s', (client_token,))
		if not duplicate and validate_building(type, sector, loc):
			data='Build:%s,%s' % (type, loc)
			event_id = sql.insert(
				'INSERT INTO `event` (`client_token`, `sector_xy`, `user_id`, `data`) VALUES (%s, %s, %s, %s)', (client_token, sector, user_id, data))
			sql.insert('INSERT INTO `structure` (`type`, `sector_xy`, `loc_xy`, `user_id`, `event_id`) VALUES (%s, %s, %s, %s, %s)', (type, sector, loc, user_id, event_id))
		if poll_afterwards:
			return poll.do_poll(str(last_id) + '^' + sector)
	else:
		return { 'success':False, 'message': "missing client token" }

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
