from serverlib import terrain
from serverlib import sql
import random


def get_inner_coords():
	r = range(20, 41)
	output = []
	for x in r:
		for y in r:
			output.append((x, y))
	random.shuffle(output)
	return output

def get_sector():
	while True:
		start_locs = sql.query("SELECT `hq_sector` AS 'sector' FROM `user`")
		bad_locs = sql.query("SELECT `sector` FROM `bad_start_location`")
		exhausted = {}
		
		for loc in start_locs + bad_locs:
			exhausted[loc['sector']] = True
		
		vacant = []
		i = 1
		while True:
			r = range(-i, i + 1)
			for dy in r:
				for dx in r:
					sector = str(dx) + '^' + str(dy)
					if not exhausted.get(sector, False):
						vacant.append(sector)
			
			if len(vacant) > 5:
				break
			else:
				vacant = []
				i += 1
		
		random.shuffle(vacant)
		
		for sector in vacant:
			sx, sy = map(int, sector.split('^'))
			for point in get_inner_coords():
				px, py = point
				
				ax = sx * 60 + px
				ay = sy * 60 + py
				
				rx, ry = terrain.toCenterRender(ax, ay)
				
				if terrain.validstart(rx, ry):
					
					return (sx, sy, px, py)
		
			sql.query("INSERT INTO `bad_start_location` (`sector`) VALUES ('" + sector + "')")
		