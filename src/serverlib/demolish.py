from serverlib import util
from serverlib import poll
from serverlib import sql

def do_demolish(user_id, last_id, sector, loc, client_token):
	#last_id = util.parseInt(last_id)
	if sector == None or loc == None: return { 'success': False, "message": "Malformed input" }
	if client_token == None: return { 'success': False, 'message': "Missing client token" }
	sx, sy = util.tuple_from_coord(sector)
	x, y = util.tuple_from_coord(loc)
	poll_afterwards = last_id > 0
	
	# TODO: distinguish between involuntary demolition and damage
	
	# get building data
	
	target = -1
	buildings = sql.query("SELECT * FROM `structure` WHERE `user_id` = " + str(user_id))
	
	for building in buildings:
		bx, by = util.tuple_from_coord(building['loc_xy'])
		bsx, bsy = util.tuple_from_coord(building['sector_xy'])
		type = building['type']
		id = building['structure_id']
		
		if type == 'hq': continue
		
		size = util.get_structure_size(type)
		
		for px in range(bx, bx + size):
			tsx = bsx + px // 60
			px = px % 60
			for py in range(by, by + size):
				tsy = bsy + py // 60
				py = py % 60
				if px == x and py == y and sx == tsx and sy == tsy:
					target = id
	
					# convert coordinates to be north corner
					sx = bsx
					sy = bsy
					x = bx
					y = by
					break
			if target != -1: break
		
		if target != -1: break
	
	if target == -1:
		return { 'success': False, 'message': "Invalid target" }
	
	building_id = target
	
	
	
	
	sector = str(sx) + '^' + str(sy)
	loc = str(x) + '^' + str(y)
	data = "Demolish:" + loc
	
	token_exists = sql.query("SELECT `event_id` FROM `event` WHERE `client_token` = %s LIMIT 1", (client_token,))
	if token_exists:
		pass
	else:
		event_id = sql.insert(' '.join([
			"INSERT INTO `event`",
			"(`sector_xy`,`client_token`,`user_id`,`data`)",
			"VALUES",
			"(%s, %s, " + str(user_id) + ", %s)"]),
			(sector, client_token, data))
		
		sql.query("DELETE FROM `structure` WHERE `structure_id` = " + str(building_id) + " LIMIT 1")
		# no polling, I guess. This gets really complex since the target can be in a different
		# sector than the original request. Let updates come through the normal polling pipeline
	return { 'success': True }
		