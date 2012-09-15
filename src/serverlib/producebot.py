from serverlib import sql
from serverlib import build
from serverlib import settings

def produce_bot(user_id, type):
	s = 0
	if type in '123':
		s = int(type)
	
	if s < 1 or s > 3:
		return { 'success': False, 'message': "Invalid args" }
	
	structures = sql.query("SELECT `type` FROM `structure` WHERE `user_id` = " + str(user_id))
	desired_type = [None, 'machinerylab', 'foundry', 'sciencelab']
	total = 0
	for structure in structures:
		if structure['type'] == desired_type:
			total += 1
	
	current = sql.query("SELECT `type_a`, `type_b`, `type_c` FROM `bots` WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	if len(current) == 0:
		current = [None, 0, 0, 0]
		sql.query("INSERT INTO `bots` (`user_id`) VALUES (" + str(user_id) + ")")
	else:
		current = current[0]
		current = [None,
			current['type_a']
			current['type_b']
			current['type_c']]
	
	max = total * 5
	
	if current[s] < max:
		cost = [None, settings.BOT_COST_1, settings.BOT_COST_2, settings.BOT_COST_3][s]
		if build.try_deplete_resources(
			cost['food'],
			cost['water'],
			cost['aluminum'],
			cost['copper'],
			cost['silicon'],
			cost['oil']):
			
			letter = ' abc'[s]
			sql.query("UPDATE `bots` SET `type_" + letter + "` = `type_" + letter + "` + 1 WHERE `user_id` = " + str(user_id) + " LIMIT 1")
			
			return { 'success': True, 'newtotal': current[s] + 1 }
		else:
			return { 'success': False, 'message': "You do not have enough resources" }
		
	else:
		return { 'success': False, 'message': "You cannot produce more bots of this type" }

def get_count(user_id):
	counts = sql.query("SELECT * FROM `bots` WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	if len(counts) == 0:
		return { 'success': True, 'a': 0, 'b': 0, 'c': 0 }
	c = counts[0]
	return { 'success': True, 'a': c['type_a'], 'b': c['type_b'], 'c': c['type_c'] }

def dispatch(user_id, a, b, c):
	counts = get_count(user_id)
	a = int(a)
	b = int(b)
	c = int(c)
	
	a = counts['a'] - a
	b = counts['b'] - b
	c = counts['c'] - c
	
	if a < 0 or b < 0 or c < 0:
		return { 'success': False, 'message': "These are not the droids you are looking for." }
	
	sql.query("UPDATE `bots` SET `type_a` = " + str(a) + ", `type_b` = " + str(b) + ", `type_c` = " + str(c) + " WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	
	return { 'success': True, 'a': a, 'b': b, 'c': c }