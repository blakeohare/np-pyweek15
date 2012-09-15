from serverlib import sql

def find_neighbors(user_id, rx, ry):
	failure = { 'success': False, 'message': "The radar seems to be broken." }
	if rx == None or ry == None:
		return failure
	
	rx = int(rx)
	ry = int(ry)
	
	players = sql.query("SELECT `user_id`, `name`, `hq_sector`, `hq_loc` FROM `user`")
	data = []
	
	youx, youy = None, None
	for player in players:
	
		sx, sy = map(int, player['hq_sector'].split('^'))
		px, py = map(int, player['hq_loc'].split('^'))
		
		x = sx * 60 + px
		y = sy * 60 + py
		
		data.append(
			[player['name'], x, y, 99999, player['user_id']])
	i = 0
	while i < len(data):
		datum = data[i]
		dx = rx - datum[1]
		dy = ry - datum[2]
		
		d = (dx * dx + dy * dy) ** .5
		datum[3] = d
		i += 1
	
	
	data.sort(key=lambda item:item[3])
	
	output = []
	
	data = data[:11]
	
	
	
	return {
		'success': True,
		'neighbors': data
	}