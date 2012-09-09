import pygame
import time
import os
from collections import defaultdict

from src import menus
from src import worldmap, settings, sprite, building
from src.font import get_text
# types: key, type, mouseleft, mouseright, mousemove
# action: left, right, up down, build, enter, demolish
event_actions = 'left, right, up down, build, enter, demolish, debug'.split(', ')
class MyEvent:
	def __init__(self, type, action, down, x, y):
		self.type = type
		self.action = action
		self.down = down
		self.up = not down
		self.x = x
		self.y = y

def get_screen():
	flags = pygame.FULLSCREEN if settings.full_screen_mode else 0
	screen = pygame.display.set_mode((settings.sx * settings.sz, settings.sy * settings.sz), flags)
	vscreen = pygame.Surface((settings.sx, settings.sy)).convert()
	return screen, vscreen

letters = {
	pygame.K_BACKSPACE: ('bs', 'bs'),
	pygame.K_TAB: ('tab', "TAB"),
	pygame.K_RETURN: ('enter', 'enter'),
	pygame.K_LEFTBRACKET: '[{',
	pygame.K_RIGHTBRACKET: ']}',
	pygame.K_SEMICOLON: ';:',
	pygame.K_QUOTE: "'"+'"',
	pygame.K_BACKSLASH: "\\|",
	pygame.K_0: '0)',
	pygame.K_1: '1!',
	pygame.K_2: '2@',
	pygame.K_3: '3#',
	pygame.K_4: '4$',
	pygame.K_5: '5%',
	pygame.K_6: '6^',
	pygame.K_7: '7&',
	pygame.K_8: '8*',
	pygame.K_9: '9(',
	pygame.K_MINUS: '-_',
	pygame.K_EQUALS: '=+',
	pygame.K_BACKQUOTE: '`~',
	pygame.K_COMMA: ",<",
	pygame.K_PERIOD: ".>",
	pygame.K_QUESTION: "/?",
	pygame.K_SPACE: '  '
}
meh = 'abcdefghijklmnopqrstuvwxyz'
for letter in range(26):
	letters[pygame.K_a + letter] = meh[letter] + meh[letter].upper()

_type_delay = [None, 0]

def toggle_full_screen():
	settings.full_screen_mode = not settings.full_screen_mode
	if settings.full_screen_mode:
		settings.sx, settings.sy, settings.sz = settings.fsx, settings.fsy, settings.fsz
	else:
		settings.sx, settings.sy, settings.sz = settings.wsx, settings.wsy, settings.wsz
	return get_screen()


# Was this supposed to go somewhere else?
class PlayScene(object):
	def __init__(self):
		self.next = self
		x0, y0 = worldmap.choosevalidstart()
		self.you = sprite.You(x0, y0)
		self.you.lookatme()
		self.sprites = [self.you]
		# Put down some random buildings OBVIOUSLY THIS IS JUST FOR TESTING
		self.buildings = []
		import random
		for j in range(100):
			x = x0 + random.randint(-50, 50)
			y = y0 + random.randint(-50, 50)
			if not worldmap.canbuildhere(x, y): continue
			Btype = random.choice([building.HQ, building.Greenhouse])
			self.buildings.append(Btype(x, y))

	def process_input(self, events, pressed):
		dx, dy = (pressed['right'] - pressed['left']), (pressed['up'] - pressed['down'])
		if dx and dy:
			dx *= 0.707
			dy *= 0.707
		self.you.move(dx, dy)

	def update(self):
		for building in self.buildings: building.update()
		for sprite in self.sprites: sprite.update()
		self.you.trackme()
		worldmap.killtime(0.01)
	
	def render(self, screen):
		worldmap.drawscene(screen, self.buildings + self.sprites)
		if settings.showminimap:
			worldmap.drawminimap(screen)

def main():
	
	pygame.init()
	rscreen, vscreen = get_screen()
	
	last_fps = 30
	# TODO: type counter
	
	scene = menus.TitleScene()  # can be set to None to quit
	pressed_keys = defaultdict(bool)
	for ea in event_actions:
		pressed_keys[ea] = False
	while scene:
		start = time.time()
		
		events = []
		pressed = pygame.key.get_pressed()
		shift = pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]
		ctrl = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]
		alt = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				scene = None
			elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
				x = vscreen.get_width() * event.pos[0] // rscreen.get_width()
				y = vscreen.get_height() * event.pos[1] // rscreen.get_height()
				if event.type == pygame.MOUSEMOTION:
					events.append(MyEvent('mousemove', None, False, x, y))
				else:
					down = event.type == pygame.MOUSEBUTTONDOWN
					left = event.button == 1
					events.append(MyEvent('mouseleft' if left else 'mouseright', None, down, x, y))
			elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
				down = event.type == pygame.KEYDOWN
				if event.key == pygame.K_ESCAPE:
					scene = None
				elif event.key == pygame.K_F4 and alt:
					scene = None
				elif event.key == pygame.K_F1:
					events.append(MyEvent('key', 'debug', down, 0, 0))
				elif event.key == pygame.K_F11 and down:
					rscreen, vscreen = toggle_full_screen()
				elif event.key == pygame.K_LEFT:
					events.append(MyEvent('key', 'left', down, 0, 0))
				elif event.key == pygame.K_RIGHT:
					events.append(MyEvent('key', 'right', down, 0, 0))
				elif event.key == pygame.K_UP:
					events.append(MyEvent('key', 'up', down, 0, 0))
				elif event.key == pygame.K_DOWN:
					events.append(MyEvent('key', 'down', down, 0, 0))
				elif event.key == pygame.K_SPACE:
					events.append(MyEvent('key', 'build', down, 0, 0))
				
				if len(events) > 0 and events[-1].type == 'key':
					pressed_keys[events[-1].action] = events[-1].down
				
				typed = letters.get(event.key, None)
				if typed != None:
					if down:
						letter = typed[shift]
						events.append(MyEvent('type', letter, True, 0, 0))
						_type_delay[0] = letter
						_type_delay[1] = 0
					else:
						_type_delay[0] = None
				
				# TODO: mouse events
		if not scene: break
		
		if _type_delay[0] != None:
			_type_delay[1] += 1
			k = _type_delay[0]
			d = _type_delay[1]
			if d > 20 and d % 3 == 0:
				events.append(MyEvent('type', k, True, 0, 0))
		
		scene.process_input(events, pressed_keys)
		scene.update()
		scene.render(vscreen)
		if settings.sz == 1:
			rscreen.blit(vscreen, (0,0))
		elif settings.sz == 2:
			pygame.transform.scale2x(vscreen, rscreen)
		else:
			pygame.transform.scale(vscreen, rscreen.get_size(), rscreen)
		
		length = time.time() - start
		if length > 0:
			rscreen.blit(get_text("FPS: %.1f" % (1.0 / length), (255, 0, 0), 18), (4, 4))
		
		pygame.display.flip()
		end = time.time()
		
		diff = end - start
		delay = 1.0 / settings.fps - diff
		if delay > 0:
			time.sleep(delay)
		else:
			last_fps = 1.0 / diff
			
		scene = scene.next
	if settings.dumpmap:
		worldmap.dumpmap()
