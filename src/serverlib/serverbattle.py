from serverlib import sql
from serverlib import settings

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