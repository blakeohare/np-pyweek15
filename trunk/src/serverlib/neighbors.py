from serverlib import sql

def find_neighbors(user_id, rx, ry):
	failure = { 'success': False, 'message': "The radar seems to be broken." }
	if rx == None or ry == None:
		return failure
	players = sql.query("SELECT `user_id`, `name`, `hq_sector`, `hq_loc` FROM `user`")
	data = []
	
	youx, youy = None, None
	for player in players:
	
		sx, sy = map(int, player['hq_sector'])
		px, py = map(int, player['hq_loc'])
		
		x = sx * 60 + px
		y = sy * 60 + py
		
		if player['user_id'] == user_id: 
			youx, youy = x, y
		else:
			data.append(
				[player['name'], x, y, 99999])
	
	if youx == None or youy == None:
		return failure
	
	i = 0
	while i < len(data):
		dx = youx - data[1]
		dy = youy - data[2]
		
		d = (dx * dx + dy * dy) ** .5
		data[3] = d
		i += 1
	
	
	data.sort(key=lambda item:item[3])
	
	output = []
	
	data = data[:10]
	
	
	
	return {
		'success': True,
		'neighbors': data
	}