from serverlib import util
from serverlib import sql

def get_user(raw_id_list):
	if raw_id_list != None:
		raw_ids = raw_id_list.split(',')
		user_lookup = {}
		ids = []
		for id in raw_ids:
			id = util.parseInt(id)
			if id > 0:
				ids.append(str(id))
		
		if len(ids) > 0:
			if len(ids) == 1:
				users_db = sql.query("SELECT `name`, `user_id` FROM `user` WHERE `user_id` = %s LIMIT 1", (ids[0],))
			else:
				users_db = sql.query("SELECT `name`, `user_id` FROM `user` WHERE `user_id` IN (" + ', '.join(ids) + ")")
			output = []
			for user in users_db:
				name = user['name']
				id = user['user_id']
				output.append((id, name))
			return { 'success': True, 'users': output }
	return { 'success': False, 'message': "User ID list is blank" }