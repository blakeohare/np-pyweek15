from src import structure
from src import worldmap
from src import camera
from src import util
from src import network
from src import border
from src import settings
from src import terrain

def max(a, b): return a if a > b else b
def min(a, b): return a if a < b else b

user_colors = [
	(255, 0, 0, 100),
	(255, 255, 0, 100),
	(255, 0, 255, 100),
	(0, 255, 0, 100),
	(0, 100, 255, 100),
	(255, 128, 0, 100)
]

class MagicPotato:
	
	def __init__(self):
		self.buildings_by_coord = {}
		self.buildings_by_sector = {}
		self.last_id_by_sector = {}
		self.player_names = {}
		self.player_name_search = []
		self.active_selection = None
		self.sector_by_user = {}
		self.user_by_sector = {}
		self.borders_by_user = {}
		self.buildings_available = {}
		self.bytes_stolen = 0
		self.unlock = False
		self.bots_owned = None
		self.deploy_request = None
		self.queue_epic_battle = False
		self.epic_battle_won = False
		
		# Hack time. Since the potato instance is a singleton, might as well make it a global :P
		global hotpotato
		hotpotato = self
		
		# There are resources and escrow resources.
		# Resources represents what the user will perceive.
		# Escrow represents the difference between perception
		# and how many resources the server thinks the user has.
		# Both of these amounts are 10x in the model as what is 
		# utlimately displayed e.g. if it says 200 here, it says 20 in the UI.
		# If the user gains resources, they are transferred to the
		# actual resources from escrow in increments of 5% per frame.
		# This will make it appear as though the stream is constant. 
		# If the user spends resources, it is subtracted immediately from the 
		# actual resources. Escrow will be set to 0. 
		
		self.resources = {
			'food': 0,
			'water': 0,
			'aluminum': 0,
			'copper': 0,
			'silicon': 0,
			'oil': 0
		}
		
		self.escrow = {
			'food': 0,
			'water': 0,
			'aluminum': 0,
			'copper': 0,
			'silicon': 0,
			'oil': 0
		}
	
	# local_mx/y is model coordinates mod 60
	def is_within_borders(self, user_id, sector_x, sector_y, local_mx, local_my, s=1):
		border = self.borders_by_user[user_id]
		for dx in range(s):
			for dy in range(s):
				if not border.iswithin(*terrain.toRender(local_mx+dx, local_my+dy)):
					return False
		return True
	
	def is_touching_other_building(self, user_id, sector_x, sector_y, target_x, target_y, building_id):
		size = structure.get_structure_size(building_id)
		buildings = self.get_all_buildings_of_player_SLOW(user_id)
		tx = int(target_x // 1)
		ty = int(target_y // 1)
		
		occupied = {}
		for building in buildings:
			x, y = building.getModelXY()
			x = int(x // 1)
			y = int(y // 1)
			bsize = structure.get_structure_size(building.btype)
			for px in range(x - 1, x + bsize + 1):
				for py in range(y - 1, y + bsize + 1):
					occupied[(px, py)] = building.btype
		
		for px in range(tx, tx + size):
			for py in range(ty, ty + size):
				if occupied.get((px, py)) != None:
					return True
					
		return False
	
	def is_within_sector(self, user_id, sector_x, sector_y, target_x, target_y, building_id):
		size = structure.get_structure_size(building_id)
		tx, ty = int(target_x // 1), int(target_y // 1)
		if tx == 59 or ty == 59:
			return False
		
		your_sector = self.sector_by_user[user_id]
		
		return sector_x == your_sector[0] and sector_y == your_sector[1]
	
	def build_within_count_limit(self, user_id, building_id):
		total = 0
		
		limit = structure.get_structure_limit(building_id)
		
		if limit == 0:
			return True
		
		for building in self.get_all_buildings_of_player_SLOW(user_id):
			if building.btype == building_id:
				total += 1
		
		if total < limit:
			return True
		
		return False
	
	def add_research(self, building_id, playscene):
		self.buildings_available[building_id] = True
		network.send_start_research(playscene.user_id, playscene.password, building_id)
	
	def starting_buildings(self, buildings):
		for building in buildings:
			self.buildings_available[building] = True
	
	def deploy_bots(self, playscene, flush=False):
		if self.deploy_request == None:
			if flush:
				self.deploy_request = network.send_deploy(playscene.user_id, playscene.password)
			else:
				self.deploy_request = network.send_getbots(playscene.user_id, playscene.password)
		#print(self.deploy_request.get_response())
		
	def deploy_success(self, clear_status=True):
		if self.deploy_request != None:
			if self.deploy_request.has_response():
				r = self.deploy_request.get_response()
				
				if clear_status:
					self.deploy_request = None
				
				if r != None:
				
					if r.get('success', False):
						return [
							r.get('a', 0),
							r.get('b', 0),
							r.get('c', 0)
						]
				return [0, 0, 0]
			else:
				return "deploying"
		return None
	
	def apply_bot_snapshot(self, a, b, c):
		self.bots_owned = [a, b, c]
	
	def is_building_available(self, type):
		if self.unlock: return True
		
		if settings.building_research.get(type) == 0:
			return True
		if self.buildings_available.get(type) == None:
			return False
		return True
	
	def buildings_to_research(self):
		b = self.bytes()
		output = []
		for key in settings.building_research.keys():
			if key == 'hq': continue
			if self.is_building_available(key):
				continue
			if settings.building_research[key] <= b:
				output.append(
					(key, settings.building_research[key]))
		
		output.sort(key=lambda x:x[1])
		return output[:3]
	
	def bytes(self):
		return self.bytes_stolen
	
	def modify_bytes(self, newbytes):
		self.bytes_stolen = newbytes
		#print (newbytes)
		a = 1 / 0
		self.building_availability_cache = None
	
	def get_resource(self, key):
		return int(self.resources[key] // 10)
	
	def try_spend_resources(self, f, w, a, c, s, o):
		if self.resources['food'] < f: return False
		if self.resources['water'] < w: return False
		if self.resources['aluminum'] < a: return False
		if self.resources['copper'] < c: return False
		if self.resources['silicon'] < s: return False
		if self.resources['oil'] < o: return False
		
		self.resources['food'] -= f
		self.resources['water'] -= w
		self.resources['aluminum'] -= a
		self.resources['copper'] -= c
		self.resources['silicon'] -= s
		self.resources['oil'] -= o
		
		return True
		
	def spend_resource(self, key, amount):
		self.resources[key] -= amount
		self.escrow[key] = 0
	
	def apply_poll_data(self, poll, you_id):
		if not poll.get('success', False): return
		
		# users that have building adds/removes
		dirty_users = {}
		
		resources = poll.get('resources', {})
		for key in resources.keys():
			latest = int(resources[key] * 10)
			self.escrow[key] = latest - self.resources[key]
		
		for sector_data in poll.get('sectors', []):
			id = util.totuple(sector_data.get('id', None))
			if sector_data.get('all', False):
				# list of all buildings
				
				#self.last_id_by_sector[id] = max(
				#	self.last_id_by_sector.get(id, 0),
				#	sector_data.get('valid_through', 0))
				
				structures = sector_data.get('structures', [])
				structures.sort(key=lambda x:x[4])
				for structure in structures:
					if len(structure) == 5:
						structure_id = structure[0]
						type = structure[1]
						loc = util.totuple(structure[2])
						owner = structure[3]
						event_id = structure[4]
						dirty_users[owner] = True
						self.sector_by_user[owner] = id
						self.user_by_sector[id] = owner
						if self.last_id_by_sector.get(id, 0) < event_id:
							self.add_structure(owner, type, id[0], id[1], loc[0], loc[1])
							self.last_id_by_sector[id] = event_id
							#if owner == you_id and type == 'launchsite':
							#	self.queue_epic_battle = True
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
							self.sector_by_user[user_id] = id
							self.user_by_sector[id] = user_id
							if datakey == 'build':
								parts = datavalue.split(',')
								if len(parts) == 2:
									type = parts[0]
									loc = util.totuple(parts[1])
									self.add_structure(user_id, type, id[0], id[1], loc[0], loc[1])
									dirty_users[user_id] = True
									if type == 'launchsite' and user_id == you_id:
										self.queue_epic_battle = True
							elif datakey == 'demolish':
								x, y = map(int, datavalue.split('^'))
								self.remove_structure(id, x, y)
								dirty_users[user_id] = True
		
		for user_id in dirty_users.keys():
			sector = self.sector_by_user.get(user_id)
			if sector != None: # should not be false, but crashes suck really bad
				buildings = self.buildings_by_sector.get(sector, [])
				color = user_colors[user_id % len(user_colors)]
				self.borders_by_user[user_id] = border.Border(color, [(b, 4.5) for b in buildings], sector)
	
	def get_borders_near_sector(self, sx, sy):
		borders = []
		for x in (-1, 0, 1):
			for y in (-1, 0, 1):
				user_id = self.user_by_sector.get((sx+x, sy+y), None)
				if user_id != None:
					border = self.borders_by_user.get(user_id, None)
					if border != None:
						borders.append(border)
		return borders

	def get_value_of_base_by_player_id(self, user_id):
		# This is how many bytes you get for attacking this base (assuming you haven't attacked it before)
		return sum(b.nbytes for b in self.get_all_buildings_of_player_SLOW(user_id))
	
	def get_value_of_attack(self, attacker_id, defender_id):
		b0 = self.get_value_of_base_by_player_id(defender_id)
		b = self.get_bytes_taken_already(attacker_id, defender_id)
		return max(b0 - b, 0)

	def get_bytes_taken_already(self, attaker_id, defender_id):
		# TODO: determine hwo many bytes we've already taken
		return 0
	
	def get_all_buildings_of_player_SLOW(self, user_id):
		# not really indexed ideally, so just iterate through all buildinsg
		# this should only be called once during battle initiation, not every frame
		buildings = []
		for building_batch in self.buildings_by_sector.values():
			for building in building_batch:
				if building.user_id == user_id:
					buildings.append(building)
		return buildings
	
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
			bx = int(bx // 1)
			by = int(by // 1)
			
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
		
		for key in self.escrow.keys():
			amt = self.escrow[key]
			if amt > 0:
				debit = self.escrow[key] * 0.01
				self.escrow[key] -= debit
				self.resources[key] += debit
			elif amt < 0:
				self.resources[key] += amt
				self.escrow[key] = 0
	
	def get_user_name(self, user_id):
		default_name = "?"*8
		name = self.player_names.get(user_id, None)
		if name == None:
			self.player_names[user_id] = default_name
			self.player_name_search.append(
				network.send_username_fetch([user_id]))
			return default_name
		return name
