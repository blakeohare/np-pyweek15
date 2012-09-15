from serverlib import sql
from serverlib import settings
from serverlib import util


def award_resources(user_id, alien_type):
	if not alien_type in ('1', '2', '3'):
		return { 'success': False, 'message': "Invalid args" }
	
	if alien_type == '1':
		award = settings.ALIEN_DROPS[0]
	elif alien_type == '2':
		award = settings.ALIEN_DROPS[1]
	else: #elif alien_type == '3':
		award = settings.ALIEN_DROPS[2]
	
	updates = []
	for key in award.keys():
		updates.append("`" + key + "` = `" + key + "` + " + str(award[key]))
	sql.query("UPDATE `resource_status` SET " + ', '.join(updates) + " WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	
	return { 'success': True }

def award_bytes(user_id, attacked_id, num_bytes):
	attacked_id = util.parseInt(attacked_id)
	num_bytes = util.parseInt(num_bytes)
	if attacked_id <= 0 or num_bytes <= 0:
		return { 'success': False, 'message': "Invalid args" }
	
	user_exists = sql.query("SELECT `user_id` FROM `user` WHERE `user_id` = " + str(attacked_id) + " LIMIT 1")
	if len(user_exists) == 0:
		return { 'success': False, 'message': "User doesn't exist. Are you a l33t hax0r?" }
	
	
	sql.query("UPDATE `user` SET `research` = `research` + " + str(num_bytes) + " WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	
	new_research = sql.query("SELECT `research` FROM `user` WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	
	return { 'success': True, 'research': new_research[0]['research'] }
	
		