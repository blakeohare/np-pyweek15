import time
from src import settings


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
		self.research = 10
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
					# Lines are this long:
					#"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
				   ["Welcome to planet Tantalus! I'm Mica,",
                     "an AI attached to the computer in your",
                     "headquarters, and I'm going to try to",
                     "help you through these first few days",
                     "on Tantalus."],
                    
                    ["Now, one of the things you organics",
                     "need to survive is food, so I suggest",
                     "you access my Build menu, then select",
                     "resources."],
                     
                    
                    ["Here you'll see a greenhouse! This",
                     "will help provide you with nutrients",
                     "and water humans require. Select the",
                     "greenhouse, and then build within the",
                     "boundaries by pressing the spacebar."]
				],
				['greenhouse'],
				[],
				0
			],
			
			[
				# challenge 1 - turrets
				"Set up a perimeter",
				[
                    ["Excellent! Now, you might have noticed",
                    "those unusual looking creatures outside",
                    "your base. I hope you haven't touched",
                    "them, because they're really quite rude",
                    "as aliens go. "],
                    
                    ["In fact, they'll attempt to damage",
                     "your squishy human body, so I",
                     "recommend not giving them the chance!"],
                    
                    ["You've been given a small ray gun for",
                    "self-defense; use it by both accessing",
                    "the Fire Ray Gun option in the menu,",
                    "or by pressing the \"Z\" key."],
                    
                    ["Go and don't let those monsters show",
                    "us exactly what you are made of!",
                    "...It's meat, right? I'm pretty sure",
                    "it's some sort of meat..."],
                     
                    ["Also, you can build turrets for base",
                    "defense. Select the Turret from the",
                    "Defensive unit menu. Build it the same",
                    "way you built the greenhouse. They'll",
                    "kill any aliens who invade your base!"],
                    
                    ["Luckily you brought 3 turrets with",
                     "you amongst your landing equipment.",
                     "Three turrets should do for now."]
				],
				['turret', 'turret', 'turret'],
				[],
				0
			],
			
			[
				# challenge 2 - research
				"Research",
				[
                     ["Here's something interesting: I found",
                     "I have a Research function, but it's",
                     "a little risky: your base will lose",
                     "shields for a bit, but if we do I can",
                     "learn some new things to let us build",
                     "foundries."],
                    
                    ["With a foundry, we can build bots,",
                    "which would increase our fighting power",
                    "dramatically!"],
                    
                    ["We're going to have to try! Get ready",
                     "for a fight! Approach headquarters",
                     "and press enter!"]
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
                     "I know how to build a foundry",
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
					 "it and press ENTER. Build bots"],
					
					["Here, have some resources to",
					 "get you started."],
				],
				[],
				[],
				5
			],
			
			[
				# challenge 5 - see neighbor
				"Neighborhood Meet-n-Greet",
				[
					 ["It looks like there's another base",
                     "towards the southeast. A base where",
                     "we can get resources and maybe even",
                     "information! Maybe you should go",
                     "meet the neighbors?"],
				],
				[],
				[],
				0
			],
			
			[
				# challenege 6 - ATTACK
				"ATTACK",
				[
				      ["Seems like our neighbors have some",
                     "awfully nice technology. Time to use",
                     "those bots! To deploy, select the",
                     "Deploy Bots option from the menu. Then"],
                     
                     ["approach a building to attack and press",
                     "1, 2, or 3 to deploy the corresponding",
                     "type of bot."],
                     
                     ["And don't worry; after all, this is a",
                     "prison planet, so everyone here is a",
                     "horrible person anyway."],
                     
                     ["Well, except you, of course!"],
				],
				[],
				[],
				0
			],
			[
				# challenge 7 - Explain research & conclusion
				"Conclusion",
				[
					  ["If you managed to bring the enemy HQ",
                     "down to one health, you'll be awarded",
                     "with bytes of data. Collect bytes to",
                     "unlock more technologies!"],
                    
                    ["Don't forget to explore my build menu,",
                     "because there's so much more! Like a",
                     "medical tent, different factories, and",
                     "ways to gather more resources."],
                     
                    ["In fact, if we gather enough resources",
                     "and technology, we might even be able",
                     "to find you a way home!"],
                     
                     ["This concludes the training mission."]
				],
				[],
				[],
				0
			]
		]
		self.last_dialog_shown = -1
	
	def get_active_dialog(self):
		if self.last_dialog_shown == self.current_step:
			return None
		else:
			self.last_dialog_shown = self.current_step
			step = self.active_step()
			return step[1]
	
	def add_building(self, type, sx, sy, x, y):
		self.buildings.append(
			(type, True, (sx * 60 + x, sy * 60 + y), len(self.buildings) + 1))
	
	def active_step(self):
		return self.steps[self.current_step]

	def update_resources(self, diff):
		for key in 'food water aluminum oil copper silicon'.split(' '):
			
			amt = 1.0 if (key in ('food', 'water')) else 0.0
			self.resources[key] = self.resources.get(key, 0) + amt * diff
			
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
	tut.last_poll = now
	
	output = { 'success': True }
	
	tut.update_resources(diff)
	
	output['resources'] = {
		'food': tut.resources.get('food', 0),
		'water': tut.resources.get('water', 0),
		'oil': tut.resources.get('oil', 0),
		'aluminum': tut.resources.get('aluminum', 0),
		'copper': tut.resources.get('copper', 0),
		'silicon': tut.resources.get('silicon', 0)
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
		step[2] = step[2][1:]
		if len(step[2]) == 0:
			tut.current_step += 1
	
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

def send_alien_award(user_id, password, alientype):
	tut = active_tutorial()
	for k,v in settings.ALIEN_DROPS[alientype-1].items():
		tut.resources[k] += v

def send_start_research(user_id, password, subject):
	# TODO: disable research from HQ before this tutorial step
	
	tut = active_tutorial()
	if tut.current_step == 2:
		tut.current_step += 1
		tut.resources['food'] += 100
		tut.resources['water'] += 100
		tut.resources['aluminum'] += 200
		tut.resources['copper'] += 200
		tut.resources['silicon'] += 200
		
		from src import data
		
		
		return FakeResponse({ 'success': True })
	else:
		return FakeResponse({ 'success': False })

def send_getbots(user_id, password):
	tut = active_tutorial()
	output = { 'success': True }
	output['a'] = tut.bots[0]
	output['b'] = tut.bots[1]
	output['c'] = tut.bots[2]
	return FakeResponse(output)

def send_buildbots(user_id, password, type):
	tut = active_tutorial()
	
	if tut.bots[0] == 3:
		return FakeResponse({ 'success': False, 'message': "Can't build more than 5" })
	
	tut.bots[0] += 1
	
	if tut.bots[0] == 3:
		
		tut.current_step += 1
	
	
	output = { 'success': True, 'a': tut.bots[0], 'b': 0, 'c': 0 }
	return FakeResponse(output)


def send_deploy(user_id, password):
	tut = active_tutorial()
	return FakeResponse({ 'success': True, 'a': tut.bots[0], 'b': 0, 'c': 0 })
	
def send_battle_success(user_id, password, attacked_id, bytes):
	
	if attacked_id == 2:
		tut = active_tutorial()
		tut.current_step += 1
	return FakeResponse({ "success": True })