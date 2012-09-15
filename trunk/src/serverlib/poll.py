from serverlib import sql

def do_poll(user_id, sector_args):
	output = { 'success': True }
	sectors = []
	for sector in sector_args.split(','):
		parts = sector.split('^')
		if len(parts) == 3: # ignore malformed input. They're probably hacking and don't really deserve a neatly formatted response.
			last_id = int(parts[0])
			sector_x = int(parts[1])
			sector_y = int(parts[2])
			sector_id = str(sector_x) + '^' + str(sector_y)
			sector_data = { 'id': sector_id }
			
			if last_id == 0:
				# need a full history, just get all structures
				sector_data['all'] = True
				structures_db = sql.query("SELECT `structure_id`,`type`,`loc_xy`,`user_id`,`event_id` FROM `structure` WHERE `sector_xy` = %s", (sector_id,))
				structures = []
				sector_data['structures'] = structures
				max_id = 1 # not a mistake
				for structure in structures_db:
					structures.append([
						structure['structure_id'],
						structure['type'],
						structure['loc_xy'],
						structure['user_id'],
						structure['event_id']])
					if max_id < structure['event_id']:
						max_id = structure['event_id']
				structures.sort(key=lambda x:x[4])
				sector_data['valid_through'] = max_id
			else:
				# need recent history, get all events after a certain point
				sector_data['all'] = False
				all_events = []
				sector_data['events'] = all_events
				events_db = sql.query("SELECT `event_id`, `client_token`, `user_id`, `data` FROM `event` WHERE `sector_xy` = %s AND `event_id` > " + str(last_id), (sector_id,))
				for event in events_db:
					data = event['data']
					client_token = event['client_token'] if event['user_id'] == user_id else None
					e = [event['event_id'], client_token, event['user_id'], data]
					all_events.append(e)
			sectors.append(sector_data)
	output['sectors'] = sectors
	
	your_buildings = sql.query("SELECT `type`, `data` FROM `structure` WHERE `user_id` = " + str(user_id))
	resources = { 'water': 0.1, 'food': 0.1, 'oil': 0.0, 'aluminum': 0.0, 'copper': 0.0, 'silicon': 0 }
	for building in your_buildings:
		if building['type'] == 'farm':
			resources['food'] += 10
		elif building['type'] == 'hq':
			pass   # No need since you can kill aliens for these
		elif building['type'] == 'resevoir':
			resources['water'] += 10
		elif building['type'] == 'greenhouse':
			resources['food'] += 3
			resources['water'] += 3
		elif building['type'] == 'drill':
			resources['oil'] += 5
		elif building['type'] == 'quarry':
			data = building['data']
			# horrible hack
			x = data.split('c')
			a = int(x[0][1:])
			x = x[1].split('s')
			c = int(x[0])
			s = int(x[1])
			resources['aluminum'] += a / 20.0
			resources['copper'] += c / 20.0
			resources['silicon'] += s / 20.0
	
	import time
	now = int(time.time())
	current = sql.query("SELECT * FROM `resource_status` WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	current = current[0]
	
	diff = now - current['last_poll']
	
	if diff > 20: diff = 20 # don't let them collect resources while they're not playing
	
	setters = []
	
	for key in resources.keys():
		resources[key] *= diff / 10.0
		resources[key] += current[key]
		if resources[key] > 1000:
			resources[key] = 1000
		setters.append("`" + key + "` = " + str(resources[key]))
	
	setters.append("`last_poll` = " + str(now))
	
	sql.query("UPDATE `resource_status` SET " + ', '.join(setters) + " WHERE `user_id` = " + str(user_id) + " LIMIT 1")
	
	output['resources'] = resources
	
	return output
	
