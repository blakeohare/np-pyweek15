from src import structure
from src import worldmap
from src import camera
from src import util
from src import network

def max(a, b): return a if a > b else b
def min(a, b): return a if a < b else b

class MagicPotato:
	
	def __init__(self):
		self.buildings_by_coord = {}
		self.buildings_by_sector = {}
		self.last_id_by_sector = {}
		self.player_names = {}
		self.player_name_search = []
		self.active_selection = None
		
	def apply_poll_data(self, poll):
		if not poll.get('success', False): return
		
		for sector_data in poll.get('sectors', []):
			id = util.totuple(sector_data.get('id', None))
			if sector_data.get('all', False):
				# list of all buildings
				
				#self.last_id_by_sector[id] = max(
				#	self.last_id_by_sector.get(id, 0),
				#	sector_data.get('valid_through', 0))
				for structure in sector_data.get('structures', []):
					if len(structure) == 5:
						structure_id = structure[0]
						type = structure[1]
						loc = util.totuple(structure[2])
						owner = structure[3]
						event_id = structure[4]
						
						if self.last_id_by_sector.get(id, 0) < event_id:
							self.add_structure(owner, type, id[0], id[1], loc[0], loc[1])
							self.last_id_by_sector[id] = event_id
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
							elif datakey == 'demolish':
								x, y = map(int, datavalue.split('^'))
								self.remove_structure(id, x, y)
	
	def get_building_selection(self, mx, my):
		
		imx = int(mx // 1)
		imy = int(my // 1)
		
		adj = (-1, 0, 1)
		
		bbc = self.buildings_by_coord
		
		buildings = []
		for dx in adj:
			for dy in adj:
				x = imx + dx
				y = imy + dy
				building = bbc.get((x, y))
				if building != None:
					buildings.append((x, y, building))
		
		b = None
		for building in buildings:
			left = building[0] - .3
			right = building[0] + 1.3
			top = building[1] - .3
			bottom = building[1] + 1.3
			
			if mx > left and mx < right and my > top and my < bottom:
				b = building[2]
				break
		
		if self.active_selection != None:
			self.active_selection.selected = False
		if b != None:
			b.selected = True
		
		self.active_selection = b
		
		return b
		
	def remove_structure(self, sector, x, y):
		x += sector[0] * 60
		y += sector[1] * 60
		
		i = 0
		buildings = self.buildings_by_sector[sector]
		while i < len(buildings):
			building = buildings[i]
			bx, by = building.getModelXY()
			if bx == x and by == y:
				self.buildings_by_sector[sector] = buildings[:i] + buildings[i + 1:]
				size = structure.get_structure_size(building.type)
				for px in range(size):
					for py in range(size):
						key = (bx + px, by + py)
						if key in self.buildings_by_coord:
							self.buildings_by_coord.pop(key)
				break
			i += 1
		
		
		
	
	def add_structure(self, user_id, type, sx, sy, x, y):
		# TODO: determine if building already exists by alternate means
		
		ax = sx * 60 + x
		ay = sy * 60 + y
		size = structure.get_structure_size(type)
		
		s = structure.create(user_id, type, ax, ay)
		sector = (sx, sy)
		#list = self.buildings_by_sector.get(sector, [])
		#self.buildings_by_sector[sector] = list
		
		north = ay
		south = ay + size - 1
		west = ax
		east = ax + size - 1
		
		sector_north = north // 60
		sector_south = south // 60
		sector_west = west // 60
		sector_east = east // 60
		
		footprint = []
		remove_these = []
		for px in range(size):
			for py in range(size):
				f = (ax + px, ay + py)
				footprint.append(f)
		
		for f in footprint:
			self.buildings_by_coord[f] = s
	
		for sector_x in range(sector_west, sector_east + 1):
			for sector_y in range(sector_north, sector_south + 1):
				list = self.buildings_by_sector.get(sector, [])
				self.buildings_by_sector[sector] = list
				list.append(s)
		
	def get_structures_for_screen(self, cx, cy):
		
		# need logic to determine which sectors are on the screen
		hackityhackhack = []
		for sector in self.buildings_by_sector.values():
			hackityhackhack += sector
		
		return hackityhackhack
	
	def update(self):
		i = 0
		while i < len(self.player_name_search):
			request = self.player_name_search[i]
			if request.has_response():
				self.player_name_search = self.player_name_search[:i] + self.player_name_search[i + 1:]
				names = request.get_response()
				if names.get('success', False):
					for user in names.get('users', []):
						id = int(user[0])
						name = user[1]
						self.player_names[id] = name
			else:
				i += 1
	
	def get_user_name(self, user_id):
		default_name = "?"*8
		name = self.player_names.get(user_id, None)
		if name == None:
			self.player_names[user_id] = default_name
			self.player_name_search.append(
				network.send_username_fetch([user_id]))
			return default_name
		return name