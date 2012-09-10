from serverlib import sql
from serverlib import build
from serverlib import util

import random
import time

# TODO: I removed crystals since we're not doing that anymore. The equivalent will need to be added.

def all_populated_sectors():
	sectors_db = sql.query("SELECT `sector_xy` FROM `structure` GROUP BY `sector_xy`")
	sectors = {}
	for sector in sectors_db:
		sectors[sector['sector_xy']] = True
	return sectors

def get_next_unoccupied():
	# TODO: make this verify that the slot you pick is not water
	occupied = all_populated_sectors()
	keys = []
	r = 1
	while True:
		open_slots = []
		# loop through the 2r by 2r grid centered about the origin
		for y in range(-r, r + 1): 
			for x in range(-r, r + 1):
				key = str(x) + '^' + str(y)
				keys.append(key)
				if not occupied.get(key, False):
					open_slots.append(key)
		if len(open_slots) > 0:
			return random.choice(open_slots)
		r += 1

def add_user(user, password):
	sector = get_next_unoccupied()
	location = str(int(random.random() * 30 + 15)) + '^' + str(int(random.random() * 30 + 15))
	user_id = sql.insert('INSERT into user (`name`, `password`, `hq_sector`, `hq_loc`) values (%s,%s,%s,%s)',(user,password,sector,location) )
	
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
	result = sql.query("SELECT `user_id`, `password`, `hq_sector`, `hq_loc` FROM `user` WHERE `name`=%s LIMIT 1",(user,) )
	if len(result) == 0:
		if register_if_new:
			add_user(user, password)
			return heavy_authenticate(user, password, False, True)
		return failure_message
	
	data = result[0]
	if data['password'] == password:
		return {
			'success': True,
			'user_id': data['user_id'],
			'hq': (data['hq_sector'], data['hq_loc']),
			'is_new': is_new
		}
	else:
		return failure_message