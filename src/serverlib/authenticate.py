from serverlib import sql

# TODO: I removed crystals since we're not doing that anymore. The equivalent will need to be added.

def add_user(user, password):
	# TODO: placement logic
	# I thought of a quick and dirty algorithm while I was in the area.
	# Feel free to ignore or modify, but just wanted to throw this out there.
	# It fills a 3x3 grid, then when that gets full, it fills a 5x5 grid, then a 7x7, so on.
	#
	# occupied = get_dictionary_of_all_sectors_with_buildings() # SELECT `loc` FROM `structure` GROUP BY `loc`
	#
	# r = 1
	# while True:
	#	open_slots = []
	#   # loop through the 2r by 2r grid centered about the origin
	#	for y in range(-r, r + 1): 
	#		for x in range(-r, r + 1):
	#			key = str(x) + '^' + str(y)
	#			if occupied.get(key, None) == None:
	#				open_lots.append(key)
	#	if len(open_slots) > 0:
	#		return random.choice(open_slots)
	#   r += 1
	# 
	sector='0^0'
	location='0^0'
	user_id=sql.insert('INSERT into user (`name`, `password`, `hq_sector`, `hq_loc`) values (%s,%s,%s,%s)',(user,password,sector,location) )
	return user_id


def light_authenticate(user_id, password):
	result = sql.query("SELECT `user_id`, `password` FROM `user` WHERE `user_id`=%s LIMIT 1",(user_id,) )
	if len(result) == 0:
		return False
	return result[0]['password'] == password

def heavy_authenticate(user, password, register_if_new=False):
	failure_message = { 'success': False, 'message': "Invalid username/password." }
	result = sql.query("SELECT `user_id`, `password`, `hq_sector`, `hq_loc` FROM `user` WHERE `name`=%s LIMIT 1",(user,) )
	if len(result) == 0:
		if register_if_new:
			add_user(user, password)
			return heavy_authenticate(user, password, False)
		return failure_message
	
	data = result[0]
	if data['password'] == password:
		return {
			'success': True,
			'user_id': data['user_id'],
			'hq': (data['hq_sector'], data['hq_loc'])
		}
	else:
		return failure_message