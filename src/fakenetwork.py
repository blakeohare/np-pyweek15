import time


class FakeResponse:
	def __init__(self, response):
		self.response = response
	
	def has_response(self):
		return True
	
	def get_response(self):
		return self.response
	
	def is_error(self):
		return False

class Tutorial:
	def __init__(self):
		global _tutorial
		_tutorial = self
		
		self.research_unlocked = {}
		self.resources = {}
		self.research = 50
		self.bots = [0, 0, 0]
		self.last_poll = time.time()
		self.first_poll = True
		
		self.buildings = [
			('hq', False, (90, 30), 1),
			('turret', False, (90, 33), 2),
			('greenhouse', False, (90, 35), 3),
			('hq', True, (30, 30), 4)
		]


		self.last_event_id = { '0^0': 4, '1^0': 3 }
		
		self.current_step = 0
		self.current_page = 0
		self.steps = [
			[
				# challenge 0 - greenhouse
				"Get some grub",
				[
					["Welcome to [planet name]. In order to ensure",
					 "your survival, blah blah blah"],
					
					["Luckily you brough some equipment with you.",
					 "This equipment is available in the build menu."],
					
					["Select the greenhouse in the resources pane",
					 "in the build menu, and place it inside your base"]
				],
				['greenhouse'],
				[],
				0
			],
			
			[
				# challenge 1 - turrets
				"Set up a perimeter",
				[
					["Now it's time to get some defenses"],
					
					["Select the turret from the defenses",
					 "menu in the build menu."],
					 
					["Three should be good."]
				],
				['turret', 'turret', 'turret'],
				[],
				0
			],
			
			[
				# challenge 2 - research
				"Research",
				[
					["Excellent work. You're a natural at",
					 "this"],
					
					["NOw it's time to do some reseach"],
					
					["Blah blah blah something about shields.",
					 "going down"]
				],
				[],
				['foundry'],
				0
			],
			
			[
				# challenge 3 - build foundry
				"To Arms",
				[
					["Phew, that was close. Now that",
					 "you know how to build a foundry",
					 "you should actually make one."],
					 
					["Select the foundry in the offensive",
					 "submenu in build menu and place it",
					 "in your base."]
				],
				['foundry'],
				[],
				0
			],
			
			[
				# challenege 4 - build 5 bots
				"Build bots",
				[
					["To enter a building, approach",
					 "it and press ENTER. Build bots"]
				],
				[],
				[],
				5
			],
			
			[
				# challenge 5 - attack neighbor
				"Neighborhood Meet-n-Greet",
				[
					["Looks like you have company to the",
					 "Southeast. Go over there."]
				],
				[],
				[],
				0
			],
			
			[
				# challenege 6 - ATTACK
				"ATTACK",
				[
					["Press the deploy bots button.",
					 "To attack, walk up to a building",
					 "and press 1, 2, or 3."],
				],
				[],
				[],
				0
			],
			[
				# challenge 7 - Explain research & conclusion
				"Conclusion",
				[
					["Mention about stealing bytes."],
					
					["Conclusion- be sure to mention",
					 " that you can research tons ",
					 "of things and eventaully build"],
					 
					["a launch pad"]
				],
				[],
				[],
				0
			]
		]
	
	def add_building(type, sx, sy, x, y):
		self.buildings.append(
			(type, True, (sx * 60 + x, sy * 60 + y), len(self.buildings) + 1))
	
	def active_step(self):
		return self.steps[self.current_step]

_tutorial = None
def active_tutorial():
	global _tutorial
	return _tutorial

def set_active_tutorial(tut):
	global _tutorial
	_tutorial = tut

def send_authenticate(username, password):
	return FakeResponse({
			'success': True,
			'user_id': 1,
			'hq': ('0^0', '30^30'),
			'is_new': False,
			'research': [],
			'buildings': [],
			'bots': [0, 0, 0]
		})

def send_poll(user_id, password, sector, last_id_by_sector):
	now = time.time()
	tut = active_tutorial()
	diff = now - tut.last_poll
	
	output = { 'success': True }
	
	output['resources'] = {
		'food': 10,
		'water': 10,
		'oil': 0,
		'aluminum': 0,
		'copper': 0,
		'silicon': 0
	}
	
	if tut.first_poll:
		tut.first_poll = False
		output['sectors'] = [
			{ 'id': '0^0',
			  'all': True,
			  'structures': [
			  
				] },
			{ 'id': '1^0',
			  'all': True,
			  'structures': [
			  
			  ] }
		]
		
		i = 0
		while i < len(tut.buildings):
			
			#('hq', False, (90, 30), 1),
			building = tut.buildings[i]
			xy = building[2]
			id = i + 1
			sx, sy = xy[0] // 60, xy[1] // 60
			loc = xy[0] % 60, xy[1] % 60
			sector_id = str(sx) + '^' + str(sy)
			output['sectors'][0 if sector_id == '0^0' else 1]['structures'].append(
				[id, building[0], str(loc[0]) + '^' + str(loc[1]), 1 if building[1] else 2, building[3]])
			
			i += 1
	else:
		output['sectors'] = [
			{ 'id': '0^0',
			  'all': False,
			  'events': [
			  
				] },
			{ 'id': '1^0',
			  'all': False,
			  'events': [
			  
			  ] }
			 ]
		
		i = 0
		while i < len(tut.buildings):
			building = tut.buildings[i]
			xy = building[2]
			id = i + 1
			sx, sy = xy[0] // 60, xy[1] // 60
			loc = xy[0] % 60, xy[1] % 60
			event_id = building[3]
			sector_id = str(sx) + '^' + str(sy)
			last_id = last_id_by_sector.get(sector_id, 0)
			user_id =  1 if building[1] else 2
			if event_id > last_id:
				output['sectors'][0 if sector_id == '0^0' else 1]['events'].append(
					[event_id, str(event_id), user_id, "Build:" + building[0] + ',' + str(loc[0]) + '^' + str(loc[1])]
				)
			i += 1
	return FakeResponse(output)
	
def send_build(user_id, password, type, sector_x, sector_y, loc_x, loc_y, sector_you_care_about, last_ids_by_sector, client_token):
	
	tut = active_tutorial()
	
	step = tut.active_step()
	
	allowed = step[2]
	
	if len(allowed) > 0 and allowed[0] == type:
		# do it
		tut.add_building(type, int(sector_x), int(sector_y), int(loc_x // 1), int(loc_y // 1))
	
	return send_poll(user_id, password, sector_you_care_about, last_ids_by_sector)
	
def send_demolish(user_id, password, sector_x, sector_y, x, y, client_token):
	return FakeResponse({'success': False, 'message': "Invalid command" })

def send_username_fetch(user_ids):
	return FakeResponse({
		'success': True,
		'users': [
			[1, "You"],
			[2, "Evil Doer"]]
	})