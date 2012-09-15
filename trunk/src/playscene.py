import pygame
import time, random

from src import camera
from src import data
from src import jukebox
from src import network
from src import settings
from src import sprite
from src import structure
from src import util
from src import worldmap
from src import terrain
from src import battle
from src import buildingmenu
from src import effects
from src import border

from src.font import get_text
from src.font import get_tiny_text
from src.images import get_image


class LoadingScene:
	def __init__(self, user_id, password, sector, loc, new, research, buildings, unlock):
		self.next = self
		self.user_id = user_id
		self.password = password
		self.counter = 0
		self.new = new
		self.sector = sector
		self.loc = loc
		self.poll = network.send_poll(user_id, password, sector, {})
		self.potato = data.MagicPotato()
		self.loading_x = 200 - get_text("Loading..", (255, 255, 255), 22).get_width() // 2
		self.potato.bytes_stolen = research
		self.potato.starting_buildings(buildings)
		self.potato.unlock = unlock
	def process_input(self, events, pressed):
		pass
	
	def update(self):
		jukebox.ensure_playing(None)
		if self.poll.has_response():
			response = self.poll.get_response()
			if response.get('success', False):
				self.potato.apply_poll_data(response)
				
				t = self.potato.resources
				self.potato.resources = self.potato.escrow
				self.potato.escrow = t
				
				self.poll = None
				self.next = PlayScene(self.user_id, self.password, self.potato, util.totuple(self.sector), util.totuple(self.loc), self.new)
			else:
				print("Something terrible has happened.")
				self.next = None
	
	def render(self, screen):
		self.counter += 1
		z = (self.counter // 15) % 4
		loading = get_text("Loading" + ("." * z), (255, 255, 255), 22)
		screen.fill((0, 0, 0))
		screen.blit(loading, (self.loading_x, 100))


class Curiosity:
	def __init__(self, user_id):
		self.counter = 0
		self.hq = structure.HQ(user_id, 0, 0)
		self.hq.landing_hack = True
	
	def update(self):
		self.counter += 1

	def is_done(self):
		return self.counter >= settings.fps * 10
	
	def get_hq_height(self):
		if self.counter < 100:
			return None
		if self.counter < 200:
			c = (self.counter - 100) / 2.0
			
			return int(100 - c * 2) * 1 // 5
		self.hq.landing_hack = False
		return 0
	
	def render_skycrane(self, screen):
		path = ('lander1.png', 'lander2.png')[(self.counter // 3) % 2]
		lander = get_image(path)
		y = 10
		if self.counter < 100:
			y = self.counter // 10
			
		x = screen.get_width() // 2 - lander.get_width() // 2 + 16
		
		if self.counter > 100 and self.counter < 230:
			y1 = y + 20
			y2 = self.hq.last_render_y
			if y2 != None:
				pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(screen.get_width() // 2 + 16, y1, 1, y2 - y1))
		
		if self.counter > 230:
			d = self.counter - 230
			x += d * 4
			y += d * 2
		
		screen.blit(lander, (x, y))
		
_resource_icons = {}
def get_resource_icon(key):
	img = _resource_icons.get(key, None)
	if img == None:
		t = get_image('resources.png')
		offset = {
			'water': 0,
			'oil': 1,
			'food': 2,
			'aluminum': 3,
			'copper': 4,
			'silicon': 5
		}
		
		img = pygame.Surface((12, 12))
		img.blit(t, (offset[key] * -12, 0))
		_resource_icons[key] = img
	return img

_dark_bg = {}
def get_dark_bg(width, height):
	img = _dark_bg.get((width, height), None)
	if img == None:
		img = pygame.Surface((width, height)).convert_alpha()
		img.fill((0, 0, 0, 160))
		_dark_bg[(width, height)] = img
	return img

class DeployBotsScene:
	def __init__(self, playscene):
		self.next = self
		self.playscene = playscene
		player = self.playscene.player
		tx, ty = terrain.nearesttile(player.x, player.y)
		self.target_user = 0
		self.mx, self.my = playscene.mousex, playscene.mousey
		
		for user_id in playscene.potato.borders_by_user.keys():
			
			bord = playscene.potato.borders_by_user[user_id]
			if (tx, ty) in bord.tiles:
				self.target_user = user_id
				break
		
		self.ok_button = None
		self.cancel_button = None
	
	def process_input(self, events, pressed):
		if pressed['back']:
			self.close_menu()
		for event in events:
			if event.type == 'mousemove':
				self.mx = event.x
				self.my = event.y
			elif event.type == 'mouseleft':
				if event.up:
					hit = None
					for button in (self.ok_button, self.cancel_button):
						if button != None:
							if self.mx >= button[0] and self.mx <= button[2] and self.my >= button[1] and self.my <= button[3]:
								hit = button
					
					if hit == self.ok_button:
						self.deploy()
					elif hit == self.cancel_button:
						self.close_menu()
	
	def deploy(self):
		if self.target_user > 0:
			buildings = self.playscene.potato.get_all_buildings_of_player_SLOW(self.target_user)
			bord = self.playscene.potato.borders_by_user[self.target_user]
			self.playscene.pendingbattle = battle.Battle(self.playscene.user_id, buildings, bord, self.target_user)
		self.close_menu()
		
	def update(self):
		self.playscene.update()
	
	def close_menu(self):
		self.next = self.playscene
		self.playscene.next = self.playscene
	
	def render(self, screen):
		width = screen.get_width()
		height = screen.get_height()
		
		self.playscene.render(screen)
		
		line_height = 10
		margin = 10
		left = margin + line_height
		bg = get_dark_bg(width - margin * 2, height - 35 - margin * 2)
		y = 35 + margin
		screen.blit(bg, (margin, y))
		y += line_height
		title = get_text("Deploy Seeker Bots", (255, 255, 255), 24)
		
		screen.blit(title, (left, y))
		y += title.get_height() + line_height
		
		show_ok = False
		
		if self.target_user == 0:
			text = get_text("You must be in another user's base to do this.", (255, 0, 0), 14)
			screen.blit(text, (left, y))
		elif self.target_user == self.playscene.user_id:
			text = [
				get_text("You can't deploy your own bots against yourself.", (255, 255, 255), 14),
				get_text("That's just silly.", (255, 0, 255), 14)]
			for t in text:
				screen.blit(t, (left, y))
				y += t.get_height() + line_height
		else:
			show_ok = True
			text = get_text("Send bots to attack: " + self.playscene.potato.get_user_name(self.target_user), (255, 255, 255), 14)
			screen.blit(text, (left, y))
			y += line_height + text.get_height()
			
			num_bytes = 298378
			x = left
			text = [
				get_text("If successful, you will gain ", (255, 255, 255), 14),
				get_text(str(num_bytes), (0, 128, 255), 16),
				get_text(" bytes of data.", (255, 255, 255), 14)]
			for t in text:
				screen.blit(t, (x, y))
				x += t.get_width()
			
			y += line_height + text[0].get_height()
			
			text = get_text("Shall we proceed?", (255, 255, 255), 18)
			screen.blit(text, (left, y))
		
		right = margin + bg.get_width()
		bottom = 35 + margin + bg.get_height()
		caption = get_text("Nevermind", (255, 255, 255), 24)
		
		bwidth = caption.get_width() + 10
		bheight = caption.get_height() + 6
		
		bleft = right - line_height - bwidth
		btop = bottom - line_height - bheight
		brect = pygame.Rect(bleft, btop, bwidth, bheight)
		hovering = self.mx >= bleft and self.mx <= bleft + bwidth and self.my >= btop and self.my < btop + bheight
		color = (0, 0, 255) if hovering else (0, 0, 0)
		
		pygame.draw.rect(screen, color, brect)
		pygame.draw.rect(screen, (255, 255, 255), brect, 1)
		screen.blit(caption, (bleft + 5, btop + 3))
		self.cancel_button = (bleft, btop, bleft + bwidth, btop + bheight)
		
		if show_ok:
			bleft = margin + line_height
			caption = get_text("FLY, MY PRETTIES!", (255, 255, 255), 24)
			
			bwidth = caption.get_width() + 10
			bheight = caption.get_height() + 6
			
			#bleft = right - line_height - bwidth
			btop = bottom - line_height - bheight
			brect = pygame.Rect(bleft, btop, bwidth, bheight)
			hovering = self.mx >= bleft and self.mx <= bleft + bwidth and self.my >= btop and self.my < btop + bheight
			color = (0, 180, 0) if hovering else (0, 0, 0)
			
			pygame.draw.rect(screen, color, brect)
			pygame.draw.rect(screen, (255, 255, 255), brect, 1)
			screen.blit(caption, (bleft + 5, btop + 3))
			
			self.ok_button = (bleft, btop, bleft + bwidth, btop + bheight)
		
			
	
		
class PlayScene:
	def __init__(self, user_id, password, potato, starting_sector, starting_xy, show_landing_sequence):
		self.curiosity = None
		if show_landing_sequence:
			self.curiosity = Curiosity(user_id)
		self.potato = potato
		self.user_id = user_id
		self.password = password
		self.next = self
		self.hq = None
		self.mousex, self.mousey = 0, 0
		self.potato.get_user_name(user_id)
		self.show_landing_sequence = show_landing_sequence
		self.cx = starting_sector[0] * 60 + starting_xy[0]
		self.cy = starting_sector[1] * 60 + starting_xy[1]

		#FIXME: this is just for testing so I can attack Blake easily - undo
#		self.cx, self.cy = terrain.toModel(-73, 0)

		self.player = sprite.You(self.cx, self.cy + 1)
		self.player.lookatme()
		self.sprites = [self.player]
		self.explored = set()   # sectors that have been populated by free-range aliens
		self.shots = []
		self.poll_countdown = 0
		self.poll = []
		self.toolbar = ToolBar(self)
		self.last_width = 400
		self.build_mode = None
		self.client_token = [
			util.md5(str(time.time()) + "client token for session" + str(self.user_id))[:10],
			1]
		self.battle = None
		self.pendingbattle = None
		self.blinkt = 0
	
	def get_new_client_token(self):
		self.client_token[1] += 1
		return self.client_token[0] + '^' + str(self.client_token[1])

	# used by sprites to determine if they can walk here
	def empty_tile(self, x, y, exclude=None):
		p = terrain.toiModel(x, y)
		b = self.potato.buildings_by_coord.get(p)
		return b == None or b is exclude
	
	def process_input(self, events, pressed):
		building_menu = False
		demolish_building = False
		attack_building = False
		if self.curiosity != None:
			pass
		else:
			direction = ''
			dx, dy = 0, 0
			if pressed['up']: dy = 1.0
			if pressed['down']: dy = -1.0
			if pressed['left']: dx = -1.0
			if pressed['right']: dx = 1.0
			
			if dx != 0 and dy != 0:
				dx *= .7071
				dy *= .7071
			
			self.player.move(dx, dy)
			# I'm moving the move logic into the sprite class so that I reuse it for aliens too. -Cosmo
			
			if self.battle:
				for event in events:
					if event.type == 'mouseleft':
						pass
					elif event.type == 'mousemove':
						pass
					elif event.type == 'key':
						if event.down and event.action == 'shoot':
							shot = self.player.shoot()
							if shot:
								self.shots.append(shot)
						elif event.down and event.action == 'build':
							if not self.battle.is_computer_attacking():
								attack_building = True
			else:
				for event in events:
					if event.type == 'mouseleft':
						if event.down:
							self.toolbar.click(event.x, event.y, self.last_width, self)
					elif event.type == 'mousemove':
						self.mousex, self.mousey = event.x, event.y
						self.toolbar.hover(event.x, event.y, self.last_width)
					elif event.type == 'key':
						if event.down and event.action == 'debug':
							buildings = self.potato.get_all_buildings_of_player_SLOW(self.user_id)
							bord = self.potato.borders_by_user[self.user_id]
							self.pendingbattle = battle.Battle(self.user_id, buildings, bord, None)
						elif event.down and event.action == 'build':
							if self.build_mode != None:
								self.build_thing(self.build_mode)
							elif self.toolbar.mode == 'demolish':
								demolish_building = True
						elif event.down and event.action == 'action':
							building_menu = True
						elif event.down and event.action == 'back':
							self.toolbar.press_back()
						elif event.down and event.action == 'shoot':
							shot = self.player.shoot()
							if shot:
								self.shots.append(shot)
					elif event.type == 'type':
						self.toolbar.accept_key(event.action, self)
						
		you_x, you_y = terrain.toModel(self.player.x, self.player.y)
		selected_building = self.potato.get_building_selection(you_x, you_y)
		
		if building_menu and selected_building != None:
			self.next = buildingmenu.BuildingMenu(self, selected_building)
		if demolish_building and selected_building != None:
			x, y = selected_building.getModelXY()
			self.blow_stuff_up(x, y)
		if attack_building and selected_building is not None:
			self.battle.attack_building(self, selected_building)
	
	def blow_stuff_up(self, x, y):
		col = util.floor(x)
		row = util.floor(y)
		sx = col // 60
		sy = row // 60
		x = col % 60
		y = row % 60
		network.send_demolish(
			self.user_id, self.password,
			sx, sy, x, y, self.get_new_client_token())
	
	def show_error(self, string):
		pass
	
	def build_thing(self, type):
		# TODO: verify you can build this item
		sx,sy = self.get_current_sector()
		x,y = self.player.getModelXY()
		client_token = self.get_new_client_token()
		
		cost = structure.get_structure_resources(type)
		
		if self.potato.try_spend_resources(
			cost['food'],
			cost['water'],
			cost['aluminum'],
			cost['copper'],
			cost['silicon'],
			cost['oil']):
			
			self.poll.append(
				network.send_build(
					self.user_id, self.password,
					type,
					util.floor(sx), util.floor(sy), util.floor(x % 60), util.floor(y % 60), (util.floor(sx), util.floor(sy)), self.potato.last_id_by_sector, client_token)
				)
			
	
	def get_current_sector(self):
		x,y = self.player.getModelXY()
		return (util.floor(x // 60), util.floor(y // 60))
	
	def update(self):
		jukebox.ensure_playing('general')
		if self.curiosity != None:
			self.curiosity.update()
			if self.curiosity.is_done():
				self.curiosity = None
		
		self.potato.update()
		self.poll_countdown -= 1
		if self.poll_countdown < 0 and len(self.poll) == 0:
			self.poll.append(network.send_poll(
				self.user_id, self.password,
				self.get_current_sector(),
				self.potato.last_id_by_sector))
		
		i = 0
		while i < len(self.poll):
			if self.poll[i].has_response():
				if not self.poll[i].is_error():
					self.potato.apply_poll_data(self.poll[i].get_response())
				self.poll = self.poll[:i] + self.poll[i + 1:]
			else:
				i += 1
		
		if len(self.poll) == 0 and self.poll_countdown < 0:
			self.poll_countdown = 10 * settings.fps
		if self.battle is None:
			worldmap.killtime(0.01)  # Helps remove jitter when exploring

		# TODO: this could just as easily be called once every 100 frames or so.
		# Populate nearby sectors with aliens
		if not self.battle:
			self.explore()
		
		if self.battle != None:
			self.battle.update(self)
			if self.battle.is_complete():
				self.pendingbattle = 17  # dummy number
		
		for s in self.sprites: s.update(self)
		self.player.update(self)
		for s in self.shots:
			s.update(self)
			s.handlealiens(self.sprites)
			if self.battle:
				s.handlealiens(self.battle.attackers)
		self.sprites = [s for s in self.sprites if s.alive]
		self.shots = [s for s in self.shots if s.alive]
		
		if not self.player.alive:
			self.player.x, self.player.y = terrain.toCenterRender(self.cx, self.cy + 1)
			self.player.healall()
			self.sprites.append(self.player)
			self.player.alive = True
		effects.update()
		
		if self.pendingbattle:
			self.blinkt += 1
			if self.blinkt >= 10:
				if self.pendingbattle == 17:   # ending a battle
					# TODO: do logic to apply results
					if self.battle:
						for building in self.battle.buildings:
							if building.destroyed:
								util.verboseprint("blowing up %s %s" % building.getModelXY())
								self.blow_stuff_up(*building.getModelXY())
						if self.battle.is_computer_attacking():
							 for building in self.battle.buildings:
							 	if building.hp > 0:
								 	building.healfull()   # TODO: charge for this valuable service
						else:
							 for building in self.battle.buildings:
							 	building.healfull()
						self.battle.hq.healfull()   # Repair the HQ after the battle
						self.battle = None
						self.pendingbattle = None
				else:   # starting a battle
					self.battle = self.pendingbattle
					self.pendingbattle = None
		elif self.blinkt:
			self.blinkt -= 1

	# populate nearby sectors and remove aliens that are too far afield
	def explore(self):
		import time
		t0 = time.time()
		sx0, sy0 = self.get_current_sector()
		# TODO: look into performance
		nexplored = set((sx0+dx, sy0+dy) for dx in (-1,0,1) for dy in (-1,0,1))
		# remove aliens that are way out there
		self.sprites = [s for s in self.sprites if s is self.player or s.getsector() in nexplored]
		# populate sectors that are newly explored
		# TODO: seed RNG based on sector so you get aliens in the same place?
		nnew = len(nexplored - self.explored)
		for sx, sy in nexplored - self.explored:
			for _ in range(4):  # TODO: more and bigger aliens depending on how far out you are.
				x, y = (sx + random.random()) * 60., (sy + random.random()) * 60.
				# TODO: don't spawn inside a base
				if not terrain.isunderwater(*terrain.toRender(x, y)):
					self.sprites.append(sprite.Alien(x, y))
		self.explored = nexplored
		if nnew:
			print("Explored %s new sectors in %.3fs" % (nnew, time.time() - t0))
	
	def summon_bots(self):
		self.next = DeployBotsScene(self)
	
	def render(self, screen):
		self.last_width = screen.get_width()
		cx = self.player.x
		cy = self.player.y
		cz = self.player.z
		camera.track(cx, cy, cz)
		structures = self.potato.get_structures_for_screen(cx, cy)
		labels = []
		
		if self.curiosity != None:
			cur = self.curiosity
			for structure in structures:
				if structure.btype == 'hq' and structure.user_id == self.user_id:
					cur.hq.x = structure.x
					cur.hq.y = structure.y
			entities = [cur.hq]
			height = cur.get_hq_height()
			if height != None:
				cur.hq.setheight(height)
			else:
				entities = []
		else:
			for structure in structures:
				if structure.btype == 'hq':
					owner_id = structure.user_id
					name = self.potato.get_user_name(owner_id)
					img = get_text(name, (255, 255, 255), 18)
					px, py = camera.screenpos(structure.x, structure.y, structure.z - 20)
					labels.append([img, px-img.get_width()//2, py])
			# Don't show destroyed buildings outside battle
			if self.battle is None:
				structure = [s for s in structures if not s.destroyed]
			entities = structures + self.sprites + self.shots
#			entities = structures + [self.player] + self.shots
			if self.battle != None:
				entities += self.battle.get_sprites()
		
		px, py = self.player.getModelXY()
		sx = int(px // 60)
		sy = int(py // 60)
		
		borders = self.potato.get_borders_near_sector(sx, sy)
		worldmap.drawscene(screen, entities + effects.effects, (cx, cy), borders)
		
		if self.curiosity != None:
			self.curiosity.render_skycrane(screen)
		
		for label in labels:
			screen.blit(label[0], (label[1], label[2]))
		if settings.showminimap:
		    worldmap.drawminimap(screen, entities)
		mx, my = self.player.getModelXY()
		lx, ly = int(mx // 1), int(my // 1)
		coords = get_text("R: (%0.1f, %0.1f) M: (%0.1f, %0.1f) L: (%i, %i)" % (cx, cy, mx, my, lx, ly), (255, 255, 0), 16)
		screen.blit(coords, (5, screen.get_height() - 25 - coords.get_height()))
		self.toolbar.render(screen)
		self.player.drawhealth(screen)

		if self.battle != None:
			self.battle.renderstatus(screen)
				
		left = 360
		top = 40
		y = top
		x = left
		for res in ('food', 'water', 'aluminum', 'copper', 'silicon', 'oil'):
			screen.blit(get_resource_icon(res), (left, y))
			screen.blit(get_text(str(self.potato.get_resource(res)), (255, 255, 255), 14), (left + 14, y))
			
			mx, my = self.mousex, self.mousey
			
			if mx > left and my > y and my < y + 20:
				newname = {
					'food': settings.RESOURCE_FOOD,
					'water': settings.RESOURCE_WATER,
					'oil': settings.RESOURCE_OIL,
					'aluminum': settings.RESOURCE_ALUMINUM,
					'copper': settings.RESOURCE_COPPER,
					'silicon': settings.RESOURCE_SILICON
				}
				img = get_text(newname[res], (255, 255, 255), 14)
				screen.blit(img, (left - 5 - img.get_width(), y + 1))
			
			y += 20

		if self.blinkt:
			h = screen.get_height()
			w = screen.get_width()
			sh = min(h * self.blinkt // 10, h // 2 + 1)
			pygame.draw.rect(screen, (0,0,0), (0,0,w,sh), 0)
			pygame.draw.rect(screen, (0,0,0), (0,h-sh,w,sh), 0)

class ToolBar:
	def __init__(self, playscene):
		self.playscene = playscene
		self.bg = None
		self.mode = 'main'
		self.hovering = -1
		buttons = {}
		self.buttons = buttons
		
		ex = {
			'build_turret': (0, 8),
			'build_farm': (0, -8),
			'build_watertreatment': (0, -11)
		}
		
		bg = get_image('toolbar/button_background.png')
		
		buttons['main_build'] = get_image('toolbar/main_build.png')
		buttons['main_demolish'] = get_image('toolbar/main_demolish.png')
		buttons['main_bots'] = get_image('toolbar/main_bots.png')
		buttons['main_exit'] = get_image('toolbar/main_exit.png')
		buttons['back'] = get_image('toolbar/back.png')
		
		
		# Caption, icon key, resulting mode, resulting lambda
		self.menu = {
			'main' : {
				'b': (1, "Build (b)", 'main_build', 'build', None),
				'd': (2, "Demolish (d)", 'main_demolish', 'demolish', None),
				'e': (3, "Deploy Bots (e)", 'main_bots', 'main', self.summon_bots)
			},
			
			'build' : {
				'r': (1, "Resource Generating (r)", 'era_landing', 'era_landing', None),
				'd': (2, "Defensive Structures (d)", 'era_lowtech', 'era_lowtech', None),
				'f': (3, "Offensive Structures (f)", 'era_medtech', 'era_medtech', None),
				's': (4, "Miscellaneous (s)", 'era_hightech', 'era_hightech', None)
				#'s': (5, "Launch", 'era_space', 'era_space', None)
			},
			
			# Landing == Resources
			'era_landing' : {
				'g': (1, "Build Green House (g)", 'build_greenhouse', 'build_greenhouse', None),
				'f': (2, "Build Farm (f)", 'build_farm', 'build_farm', None),
				'd': (3, "Build Drill (d)", 'build_drill', 'build_drill', None),
				'r': (4, "Build Resevoir (r)", 'build_resevoir', 'build_resevoir', None),
				'q': (5, "Build Quarry (q)", 'build_quarry', 'build_quarry', None)
			},
			
			# LowTech == Defense
			'era_lowtech' : {
				'b': (1, "Build Beacon (b)", 'build_beacon', 'build_beacon', None),
				't': (2, "Build Basic Turret (t)", 'build_turret', 'build_turret', None),
				'f': (3, "Build Fire Turret (f)", 'build_fireturret', 'build_fireturret', None),
				's': (4, "Build Tesla Turret (s)", 'build_teslaturret', 'build_teslaturret', None),
				'z': (5, "Build Laz0r Turret (z)", 'build_lazorturret', 'build_lazorturret', None)
			},
			
			# Med Tech == Offense
			'era_medtech' : {
				'a': (1, "Build Machinery Lab (a)", 'build_machinerylab', 'build_machinerylab', None),
				's': (2, "Build Science Lab (s)", 'build_sciencelab', 'build_sciencelab', None),
				'f': (3, "Build Foundry (f)", 'build_foundry', 'build_foundry', None)
			},
			
			# High Tech == Misc
			'era_hightech' : {
				'e': (1, "Build Medical Tent (e)", 'build_medicaltent', 'build_medicaltent', None),
				'r': (2, "Build Radar (r)", 'build_radar', 'build_radar', None),
				's': (3, "Build Launch Site (s)", 'build_launchsite', 'build_launchsite', None)
			},
			
			'era_space' : {
			}
		}
		
		self.tiny_captions = {
			'era_landing': "Resource",
			'era_lowtech': "Defensive",
			'era_medtech': "Offensive",
			'era_hightech': "Misc.",
			'era_space': "Launch Site",
			'main_build': "Build",
			'main_demolish': "Demolish",
			'main_bots': "Deploy Bots",
			'build_greenhouse': "Greenhouse",
			'build_medicaltent': "Med. Tent",
			'build_turret': "Turret",
			'build_beacon': "Beacon",
			'build_farm': "Farm",
			'build_resevoir': "Resevoir",
			'build_fireturret': "Fire Tur.",
			'build_drill': "Drill",
			'build_quarry': "Quarry",
			'build_foundry': "Foundry",
			'build_radar': "Radar",
			'build_teslaturret': "Tesla Tur.",
			'build_machinerylab': "Mach. Lab",
			'build_lazorturret': "Lazor Tur.",
			'build_sciencelab': "Science Lab",
			'build_launchsite': "Launch Site"
		}
		
		eras = structure.get_eras()
		for era in self.menu.keys():
			if era.startswith('era_'):
				for building in eras[era.split('_')[1]]:
					img = pygame.Surface(bg.get_size())
					img.blit(bg, (0, 0))
					b = get_image('buildings/' + building[0] + '.png')
					e = ex.get('build_' + building[0], (0, 0))
					img.blit(b, (img.get_width() // 2 - b.get_width() // 2 + e[0], e[1] + img.get_height() // 2 - b.get_height() // 2))
					buttons['build_' + building[0]] = img
		
		buttons['era_landing'] = buttons['build_medicaltent']
		buttons['era_lowtech'] = buttons['build_farm']
		buttons['era_medtech'] = buttons['build_radar']
		buttons['era_hightech']= buttons['build_lazorturret']
		buttons['era_space']   = buttons['build_launchsite']
		buttons['locked'] = get_image('toolbar/locked.png')
		self.details_bg = None
		self.caption_bg = None

	
	def summon_bots(self, playscene):
		playscene.summon_bots()
	
	def create_bg(self, screen):
		if self.bg == None or self.bg.get_width() != screen.get_width():
			self.bg = pygame.Surface((screen.get_width(), 35), pygame.SRCALPHA)
			self.bg.fill((0, 0, 0, 150))
	
	def find_button(self, x, y, screen_width):
		if y < 35:
			if x < 30:
				return 0
			if self.mode == 'main' and x > screen_width - 60:
				return 100
			x -= 30
			x = x // 60
			return x + 1
		return -1
	
	def accept_key(self, key, playscene):
		menu = self.menu.get(self.mode, {})
		item = menu.get(key, None)
		if item != None:
			self.select_item(item, playscene)
		
	
	def click(self, x, y, screen_width, playscene):
		id = self.find_button(x, y, screen_width)
		if id == 0:
			self.press_back()
		elif id == 100 and self.mode == 'main':	
			self.press_exit(playscene)
		elif id > 0:
			self.press_button(id, playscene)
	
	def press_exit(self, playscene):
		playscene.next = None
		
	def hover(self, x, y, screen_width):
		self.hovering = self.find_button(x, y, screen_width)
		
	def press_back(self):
		if self.mode == 'main':
			pass # how did you get here?
		elif self.mode in ('build', 'demolish'):
			self.mode = 'main'
		elif self.mode.startswith('era_'):
			self.mode = 'build'
		elif self.mode.startswith('build_'):
			id = self.mode.split('_')[1]
			s = structure.get_structure_by_id(id)
			self.mode = 'era_' + s[1]
		
	
	def is_available(self, id, playscene):
		if id.startswith('build_'):
			if playscene.potato.is_building_available(id.split('_')[1]):
				return True
			return False
		return True
	
	def select_item(self, item, playscene):
		if self.is_available(item[2], playscene):
			action = item[4]
			next_mode = item[3]
			
			if action != None:
				action(playscene)
			
			self.mode = next_mode
			
			playscene.build_mode = None
			if self.mode.startswith('build_'):
				playscene.build_mode = self.mode.split('_')[1]
	
	def press_button(self, column, playscene):
		playscene.build_mode = None
		
		active_menu = self.menu.get(self.mode, {})
		
		for item in active_menu.values():
			if item[0] == column:
				self.select_item(item, playscene)
				break
				
	
	def render_action_menu(self, screen, caption, button_id):
		text = get_text(caption, (255, 255, 255), 24)
		
		screen.blit(text, (40, 9))
		button = self.buttons[button_id]
		r = screen.blit(button, (screen.get_width() - button.get_width() - 8, 5))
		pygame.draw.rect(screen, (0, 128, 255), r, 1)
			
	
	def render(self, screen):
		self.create_bg(screen)
		screen.blit(self.bg, (0, 0))
		y = 5
		
		menu = self.menu.get(self.mode, None)
		if menu == None and self.mode.startswith('build_'):
			id = self.mode.split('_')[1]
			s = structure.get_structure_by_id(id)
			self.render_action_menu(screen, "Build " + s[11], 'build_' + id)
			# TODO: show costs
		elif menu == None:
			if self.mode == 'demolish':
				self.render_action_menu(screen, "Demolish Building", 'main_demolish')
		else:
			for key in menu.keys():
				item = menu[key]
				index = item[0]
				caption = item[1]
				button_key = item[2]
				
				if self.is_available(button_key, self.playscene):
					
					self.draw_button(button_key, index, screen, caption, key.upper())
					if self.hovering == index:
						self.render_details_menu(item, screen)
				else:
					self.draw_button('locked', index, screen, "", "")
					if self.hovering == index:
						self.render_details_menu((index, "Conduct Research to Unlock", 'locked', 'locked', None), screen)
		
		if self.mode != 'main':
			self.draw_button('back', 0, screen, "Back (ESC)")
	
	def render_details_menu(self, item, screen):
		target = item[2]
		width = 150
		top = 40
		height = 100
		bottom = top + height
		left = 5
		right = 395 - width
		dx = (right - left) // 5
		left = left + dx * (item[0] - 1)
		
		if target.startswith('build_'):

			structure_id = target.split('_')[1]
			s = structure.get_structure_by_id(structure_id)
			
			if self.details_bg == None:
				self.details_bg = pygame.Surface((width, height), pygame.SRCALPHA)
				self.details_bg.fill((0, 0, 0, 150))
			
			screen.blit(self.details_bg, (left, top))
			title = get_text(structure.get_structure_name(structure_id), (255, 255, 255), 18)
			screen.blit(title, (left + 5, top + 5))
			
			y = top + 5 + title.get_height() + 5
			description = []
			for line in structure.get_structure_description(structure_id).split('|'):
				img = get_text(line, (255, 255, 255), 14)
				screen.blit(img, (left + 5, y))
				y += img.get_height() + 4
			
			resources = structure.get_structure_resources(structure_id)
			counts = []
			for key in resources.keys():
				counts.append((key, resources[key]))
			counts.sort(key=lambda x:x[1])
			counts = counts[::-1]
			
			x = left + 5
			y = bottom - 5 - 12
			for count in counts:
				key = count[0]
				amount = count[1]
				if amount == 0:
					break
				img = get_resource_icon(key)
				screen.blit(img, (x, y))
				x += 3 + img.get_width()
				img = get_text(str(amount), (255, 255, 255), 14)
				screen.blit(img, (x, y))
				x += 8 + img.get_width()
		else:
			caption = None
			if target.startswith('era_'):
				if target == 'era_landing':
					caption = "Resource Generating"
				elif target == 'era_lowtech':
					caption = "Defensive Structures"
				elif target == 'era_medtech':
					caption = "Offensive Structures"
				elif target == 'era_hightech':
					caption = "Miscellaneous"
				else:
					caption = "Space Travel"
			elif target == 'main_demolish':
				caption = "Demolish Building"
			elif target == 'main_build':
				caption = "Build Structure"
			elif target == 'main_bots':
				caption = "Deploy Bots"
			elif target == 'locked':
				caption = "Research to Unlock"
			
			if caption != None:
				text = get_text(caption, (255, 255, 255), 18)
				height = text.get_height() + 10
				if self.caption_bg == None:
					self.caption_bg = pygame.Surface((width + 12, height), pygame.SRCALPHA)
					self.caption_bg.fill((0, 0, 0, 150))
				
				screen.blit(self.caption_bg, (left, top))
				screen.blit(text, (left + 5, top + 5))
				
			
	def draw_button(self, id, index, screen, caption, hotkey=None):
		y = 5
		hide_border = False
		if index == 0:
			x = 2
			hide_border = True
		elif index == 100:
			x = screen.get_width() - 50
		else:
			x = 40 + 60 * (index - 1)
		
		screen.blit(self.buttons[id], (x, y))
		if not hide_border:
			pygame.draw.rect(
				screen,
				(255, 255, 255) if self.hovering == index else (128, 128, 128),
				pygame.Rect(x, y, 40, 24),
				1)
		
		if hotkey != None:
			screen.blit(get_text(hotkey.upper(), (255, 255, 255), 12), (x + 40, y + 15))
			tc = self.tiny_captions.get(id, None)
			if tc != None:
				screen.blit(get_tiny_text(tc), (x, y + 23))
