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
						structure['user_id']])
					if max_id < structure['event_id']:
						max_id = structure['event_id']
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
	
	return output
	