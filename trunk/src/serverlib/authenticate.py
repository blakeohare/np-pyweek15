from serverlib import sql
from serverlib import build
from serverlib import util


import random
import time

def get_next_start_point():
	from serverlib import startingpoint
	return startingpoint.get_sector()
	
def add_user(user, password):
	user = util.trim(user)
	login_id = util.alphanums(user)
	
	if len(login_id) == 0:
		return 0
	
	start = get_next_start_point()
	
	sector = str(start[0]) + '^' + str(start[1])
	location = str(start[2]) + '^' + str(start[3])
	
	user_id = sql.insert('INSERT INTO `user` (`name`, `login_id`, `password`, `hq_sector`, `hq_loc`, `research`) values (%s,%s,%s,%s,%s, 20)',
		(user, login_id, password, sector, location))
	
	sql.insert("INSERT INTO `resource_status` (`user_id`) VALUES (" + str(user_id) + ")")
	# place HQ
	build.do_build(
		user_id,
		util.md5(str(time.time()) + "automated")[:16],
		0,
		sector,
		location,
		'hq',
		False)
	
	return user_id


def light_authenticate(user_id, password):
	result = sql.query("SELECT `user_id`, `password` FROM `user` WHERE `user_id`=%s LIMIT 1",(user_id,) )
	if len(result) == 0:
		return False
	return result[0]['password'] == password

def heavy_authenticate(user, password, register_if_new=False, is_new=False):
	failure_message = { 'success': False, 'message': "Invalid username/password." }
	login_id = util.alphanums(user)
	result = sql.query("SELECT `user_id`, `password`, `hq_sector`, `hq_loc`, `research` FROM `user` WHERE `login_id`=%s LIMIT 1",(login_id,) )
	if len(result) == 0:
		if register_if_new:
			user_id = add_user(user, password)
			if user_id == 0:
				return { 'success': False, 'message': "Could not register account. Usernames must have at least 1 alphanumeric character" }
			return heavy_authenticate(user, password, False, True)
		return failure_message
	
	data = result[0]
	
	user_id = data['user_id']
	buildings_db = sql.query("SELECT `type` FROM `research_unlocked` WHERE `user_id` = " + str(user_id))
	buildings = []
	for building in buildings_db:
		buildings.append(building['type'])
	
	bots_db = sql.query("SELECT * FROM `bots` WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	if len(bots_db) == 0:
		bots = [0, 0, 0]
	else:
		row = bots_db[0]
		bots = [row['type_a'], row['type_b'], row['type_c']]
	
	if data['password'] == password:
		return {
			'success': True,
			'user_id': data['user_id'],
			'hq': (data['hq_sector'], data['hq_loc']),
			'is_new': is_new,
			'research': data['research'],
			'buildings': buildings,
			'bots': bots
		}
	else:
		return failure_message