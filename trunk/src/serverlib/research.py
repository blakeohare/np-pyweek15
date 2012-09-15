from serverlib import sql
from serverlib import settings

def apply_research(user_id, type):
	bytes_known = sql.query("SELECT `research` FROM `user` WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	bytes_known = bytes_known[0]['research']
	cost = settings.building_research.get(type, None)
	if cost == None:
		return { 'success': False, 'message': "Invalid building type" }
	if bytes_known < cost:
		return { 'success': False, 'message': "Insufficient Data" }
	
	already = sql.query("SELECT `user_id` FROM `research_unlocked` WHERE `user_id` = " + str(user_id)  + " AND `type` = '" + str(type) + "' LIMIT 1")
	if len(already) == 0:
		sql.query("INSERT INTO `research_unlocked` (`user_id`, `type`) VALUES (" + str(user_id) + ", '" + str(type) + "')")
	return { 'success': True }
	