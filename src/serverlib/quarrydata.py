from serverlib import sql

def get_quarry_data(user_id, sector, xy):
	if sector == None or xy == None:
		return { 'success': False, 'message': "Invalid args" }
	
	buildings = sql.query("SELECT `type`, `sector_xy`, `loc_xy`, `user_id`, `data` FROM `structure` WHERE `user_id` = " + str(user_id))
	quarry = None
	for building in buildings:
		if building['type'] == 'quarry':
			if building['sector_xy'] == sector and building['loc_xy'] == xy:
				quarry = building
				break
	
	if quarry == None:
		return { 'success': False, 'message': "Quarry Not Found" }
	
	data = quarry['data']
	
	x = data.split('c')
	a = int(x[0][1:])
	x = x[1].split('s')
	c = int(x[0])
	s = int(x[1])
	
	return { 'success': True, 'a': a, 'c': c, 's': s }
	
	