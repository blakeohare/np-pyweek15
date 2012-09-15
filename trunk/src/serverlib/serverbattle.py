from serverlib import sql

def award_resources(user_id, alien_type):
	if not alien_type in ('1', '2', '3'):
		return { 'success': False, 'message': "Invalid args" }
	
	if alien_type == '1':
		award = { 'food': 25, 'aluminum': 10, 'copper': 5, 'silicon': 15 }
	elif alien_type == '2':
		award = { 'food': 50, 'water': 100, 'aluminum': 0, 'copper': 10, 'silicon': 50 }
	else: #elif alien_type == '3':
		award = { 'oil': 150, 'silicon': 100 }
	
	updates = []
	for key in award.keys():
		updates.append("`" + key + "` = `" + key + "` + " + str(award[key]))
	sql.query("UPDATE `resource_status` SET " + ', '.join(updates) + " WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	
	return { 'success': True }