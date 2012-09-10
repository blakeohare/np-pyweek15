from src import structure
from src import worldmap
from src import camera
from src import util

_size = {
	'farm': 2
}

def max(a, b): return a if a > b else b
def min(a, b): return a if a < b else b

class MagicPotato:
	
	def __init__(self):
		self.buildings_by_coord = {}
		self.buildings_by_sector = {}
		self.last_id_by_sector = {}
	
	def apply_poll_data(self, poll):
		for sector_data in poll.get('sectors', []):
			id = util.totuple(sector_data.get('id', None))
			if sector_data.get('all', False):
				# list of all buildings
				self.last_id_by_sector[id] = max(
					self.last_id_by_sector.get(id, 0),
					sector_data.get('valid_through', 0))
				for structure in sector_data.get('structures', []):
					if len(structure) == 4:
						structure_id = structure[0]
						type = structure[1]
						loc = util.totuple(structure[2])
						owner = structure[3]
						self.add_structure(owner, type, id[0], id[1], loc[0], loc[1])
			else:
				# list of new events
				events = sector_data.get('events', [])
				events.sort(key=lambda x:x[0])
				
				for event in events:
					# TODO: pending buildings
					event_id = event[0]
					if event_id > self.last_id_by_sector.get(id, 0):
						self.last_id_by_sector[id] = event_id
						client_token = event[1]
						user_id = event[2]
						data = event[3]
						parts = data.split(':')
						if len(parts) > 1:
							datakey = parts[0].lower()
							datavalue = ':'.join(parts[1:])
							if datakey == 'build':
								parts = datavalue.split(',')
								if len(parts) == 2:
									type = parts[0]
									loc = util.totuple(parts[1])
									self.add_structure(user_id, type, id[0], id[1], loc[0], loc[1])
			
	
	def add_structure(self, user_id, type, sx, sy, x, y):
		#if self.buildings_by_id.get(id, None) != None: return
		# TODO: determine if building already exists by alternate means
		
		ax = sx * 60 + x
		ay = sy * 60 + y
		size = _size.get(type, 1)
		
		s = structure.create(type, ax, ay)
		sector = (sx, sy)
		list = self.buildings_by_sector.get(sector, [])
		self.buildings_by_sector[sector] = list
		
		north = ay
		south = ay + size - 1
		west = ax
		east = ax + size - 1
		
		sector_north = north // 60
		sector_south = south // 60
		sector_west = west // 60
		sector_east = east // 60
		
		for sector_x in range(sector_west, sector_east + 1):
			for sector_y in range(sector_north, sector_south + 1):
				list = self.buildings_by_sector.get(sector, [])
				self.buildings_by_sector[sector] = list
				list.append(s)
		
		for x in range(x, x + size):
			for y in range(y, y + size):
				self.buildings_by_coord[(x, y)] = s
	
	def get_structures_for_screen(self, cx, cy):
		
		# need logic to determine which sectors are on the screen
		hackityhackhack = []
		for sector in self.buildings_by_sector.values():
			hackityhackhack += sector
		
		return hackityhackhack