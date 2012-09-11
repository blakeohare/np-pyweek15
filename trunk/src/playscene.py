import pygame
import time

from src import camera
from src import data
from src import network
from src import settings
from src import sprite
from src import structure
from src import util
from src import worldmap
from src import terrain

from src.font import get_text
from src.images import get_image


class LoadingScene:
	def __init__(self, user_id, password, sector, loc, new):
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
	
	def process_input(self, events, pressed):
		pass
	
	def update(self):
		if self.poll.has_response():
			response = self.poll.get_response()
			if response.get('success', False):
				self.potato.apply_poll_data(response)
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
		
class PlayScene:
	def __init__(self, user_id, password, potato, starting_sector, starting_xy, show_landing_sequence):
		self.potato = potato
		self.user_id = user_id
		self.password = password
		self.next = self
		self.hq = None
		self.show_landing_sequence = show_landing_sequence
		self.cx = starting_sector[0] * 60 + starting_xy[0]
		self.cy = starting_sector[1] * 60 + starting_xy[1]
		self.player = sprite.You(self.cx, self.cy + 1)
		self.sprites = [self.player]
		self.poll_countdown = 0
		self.poll = []
		self.toolbar = ToolBar()
		self.last_width = 400
		self.build_mode = None
		self.client_token = [
			util.md5(str(time.time()) + "client token for session" + str(self.user_id))[:10],
			1]
	
	def get_new_client_token(self):
		self.client_token[1] += 1
		return self.client_token[0] + '^' + str(self.client_token[1])
	
	def process_input(self, events, pressed):
		direction = ''
		dx, dy = 0, 0
		v = .15
		if pressed['up']: dy += v
		if pressed['down']: dy -= v
		if pressed['left']: dx -= v
		if pressed['right']: dx += v
		
		self.player.x += dx
		self.player.y += dy
		
		for event in events:
			if event.type == 'mouseleft':
				if event.down:
					self.toolbar.click(event.x, event.y, self.last_width, self)
			elif event.type == 'mousemove':
				self.toolbar.hover(event.x, event.y, self.last_width)
			elif event.type == 'key':
				if event.down and event.action == 'build':
					if self.build_mode != None:
						self.build_thing(self.build_mode)
					elif self.toolbar.mode == 'demolish':
						x, y = self.player.getModelXY()
						
						self.blow_stuff_up(x, y)
	
	def blow_stuff_up(self, x, y):
		col = int(x)
		row = int(y)
		sx = col // 60
		sy = row // 60
		x = col % 60
		y = row % 60
		network.send_demolish(
			self.user_id, self.password,
			sx, sy, x, y, self.get_new_client_token())
	
	def build_thing(self, type):
		# TODO: verify you can build this item
		sx,sy = self.get_current_sector()
		x,y = self.player.getModelXY()
		client_token = self.get_new_client_token()
		self.poll.append(
			network.send_build(
				self.user_id, self.password,
				type,
				int(sx), int(sy), int(x % 60), int(y % 60), (int(sx), int(sy)), self.potato.last_id_by_sector, client_token)
			)
			
	
	def get_current_sector(self):
		x,y = self.player.getModelXY()
		return (int(x // 60), int(y // 60))
	
	def update(self):
		self.potato.update()
		self.player.update()
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
		worldmap.killtime(0.01)  # Helps remove jitter when exploring
		
	def render(self, screen):
		self.last_width = screen.get_width()
		cx = self.player.x
		cy = self.player.y
		camera.lookat(cx, cy)
		structures = self.potato.get_structures_for_screen(cx, cy)
		labels = []
		for structure in structures:
			if structure.btype == 'hq':
				owner_id = structure.user_id
				name = self.potato.get_user_name(owner_id)
				img = get_text(name, (255, 255, 255), 18)
				labels.append([
					img,
					(structure.x - cx) * 16 + 200 - img.get_width() // 2,
					(-structure.y + cy) * 8 + 150 + 40])
		entities = structures + self.sprites
		worldmap.drawscene(screen, entities, (cx, cy))
		for label in labels:
			screen.blit(label[0], (label[1], label[2]))
		if settings.showminimap:
		    worldmap.drawminimap(screen, entities)
		# Note: integer coordinates are at the center of tiles, not at the corners of tiles.
		# So if you just take int(mx), int(my), you'll round down to the wrong tile sometimes.
		# A better way to do this is probably terrain.toModel(*terrain.nearesttile(cx, cy))
		mx, my = self.player.getModelXY()
		mx = int(mx * 100) / 100
		my = int(my * 100) / 100
		cx = int(cx * 100) / 100
		cy = int(cy * 100) / 100
		coords = get_text("R: (%0.1f, %0.1f) M: (%0.1f, %0.1f)"%(cx, cy, mx, my), (255, 255, 0), 16)
		screen.blit(coords, (5, screen.get_height() - 5 - coords.get_height()))
		self.toolbar.render(screen)

class ToolBar:
	def __init__(self):
		self.bg = None
		self.mode = None
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
		buttons['main_exit'] = get_image('toolbar/main_exit.png')
		buttons['back'] = get_image('toolbar/back.png')
		
		eras = structure.get_eras()
		for era in eras.keys():
			for building in eras[era]:
				img = pygame.Surface(bg.get_size())
				img.blit(bg, (0, 0))
				b = get_image('buildings/' + building[0] + '.png')
				e = ex.get('build_' + building[0], (0, 0))
				img.blit(b, (img.get_width() // 2 - b.get_width() // 2 + e[0], e[1] + img.get_height() // 2 - b.get_height() // 2))
				buttons['build_' + building[0]] = img
		
		buttons['era_landing'] = buttons['build_medicaltent']
		buttons['era_agriculture'] = buttons['build_farm']
		
	def create_bg(self, screen):
		if self.bg == None or self.bg.get_width() != screen.get_width():
			self.bg = pygame.Surface((screen.get_width(), 35), pygame.SRCALPHA)
			self.bg.fill((0, 0, 0, 150))
	
	def find_button(self, x, y, screen_width):
		if y < 35:
			if x < 30:
				return 0
			if x > screen_width - 60:
				return 100
			x -= 30
			x = x // 60
			return x + 1
		return -1
	
	def click(self, x, y, screen_width, playscene):
		id = self.find_button(x, y, screen_width)
		if id == 0:
			self.press_back()
		elif id == 100 and self.mode == None:	
			self.press_exit(playscene)
		elif id > 0:
			self.press_button(id, playscene)
	
	def press_exit(self, playscene):
		playscene.next = None
		
	def hover(self, x, y, screen_width):
		self.hovering = self.find_button(x, y, screen_width)
		
	def press_back(self):
		if self.mode == None:
			pass # how did you get here?
		elif self.mode in ('build', 'demolish'):
			self.mode = None
		elif self.mode.startswith('era_'):
			self.mode = 'build'
		elif self.mode.startswith('build_'):
			id = self.mode.split('_')[1]
			s = structure.get_structure_by_id(id)
			self.mode = 'era_' + s[1]
		
	
	def press_button(self, column, playscene):
		playscene.build_mode = None
		if self.mode == None:
			if column == 1:
				self.mode = 'build'
			elif column == 2:
				self.mode = 'demolish'
		elif self.mode == 'build':
			if column == 1:
				self.mode = 'era_landing'
			elif column == 2:
				self.mode = 'era_agriculture'
		elif self.mode.startswith('era_'):
			era = self.mode.split('_')[1]
			structures = structure.get_eras()[era]
			index = column - 1
			if index < len(structures):
				s = structures[index]
				self.mode = 'build_' + s[0]
				playscene.build_mode = s[0]
				# TODO: verify you have resources
				# Otherwise play an error noise and a 
				# "You require more vespene gas"
				
	
	def render(self, screen):
		self.create_bg(screen)
		screen.blit(self.bg, (0, 0))
		y = 5
		if self.mode == None:
			self.draw_button('main_build', 1, screen)
			self.draw_button('main_demolish', 2, screen)
			self.draw_button('main_exit', 100, screen)
		elif self.mode == 'build':
			self.draw_button('back', 0, screen)
			self.draw_button('era_landing', 1, screen)
			self.draw_button('era_agriculture', 2, screen)
		elif self.mode == 'demolish':
			self.draw_button('back', 0, screen)
			text = get_text("Demolish", (255, 255, 255), 24)
			screen.blit(text, (40, 9))
		elif self.mode.startswith('era'):
			era = self.mode.split('_')[1]
			structures = structure.get_eras()[era]
			self.draw_button('back', 0, screen)
			i = 1
			for s in structures:
				self.draw_button('build_' + s[0], i, screen)
				i += 1
			
		elif self.mode.startswith('build_'):
			id = self.mode.split('_')[1]
			s = structure.get_structure_by_id(id)
			self.draw_button('back', 0, screen)
			text = get_text("Build " + s[7], (255, 255, 255), 24)
			screen.blit(text, (40, 9))
			button = self.buttons['build_' + id]
			r = screen.blit(button, (screen.get_width() - button.get_width() - 8, 5))
			pygame.draw.rect(screen, (0, 128, 255), r, 1)
			# TODO: show costs
			
			
	def draw_button(self, id, index, screen):
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
			
		
