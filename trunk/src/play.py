import pygame
import time
import os
from collections import defaultdict

from src import menus
from src import worldmap
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

full_screen_mode = True

letters = {
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

_type_delay = {}

def toggle_full_screen():
	global full_screen_mode
	full_screen_mode = not full_screen_mode
	if full_screen_mode:
		screen = pygame.display.set_mode((1024, 768), pygame.FULLSCREEN)
	else:
		screen = pygame.display.set_mode((800, 600))
	return screen

def main():
	
	pygame.init()
	rscreen = toggle_full_screen()
	vscreen = pygame.Surface((400, 300))
	
	fps = 30
	last_fps = 30
	# TODO: type counter
	
	scene = menus.TitleScene()
	pressed_keys = defaultdict(bool)
	for ea in event_actions:
		pressed_keys[ea] = False
	while True:
		start = time.time()
		
		events = []
		pressed = pygame.key.get_pressed()
		shift = pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]
		ctrl = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]
		alt = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
			elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
				down = event.type == pygame.KEYDOWN
				if event.key == pygame.K_ESCAPE:
					return
				elif event.key == pygame.K_F4 and alt:
					return
				elif event.key == pygame.K_F1:
					events.append(MyEvent('key', 'debug', down, 0, 0))
				elif event.key == pygame.K_F11 and down:
					rscreen = toggle_full_screen()
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
						_type_delay[letter] = 0
					else:
						if _type_delay.get(letter) != None:
							_type_delay.pop(letter)
				
				# TODO: mouse events
		
		for k in _type_delay.keys():
			_type_delay[k] += 1
			d = _type_delay[k]
			if d > 20 and d % 3 == 0:
				events.append(MyEvent('type', k, True, 0, 0))
		
		scene.process_input(events, pressed_keys)
		scene.update()
		scene.render(vscreen)
		
		pygame.transform.scale(vscreen, rscreen.get_size(), rscreen)
		
		length = time.time() - start
		if length > 0:
			rscreen.blit(get_text("FPS: " + str(1.0 / length), (255, 0, 0), 18), (4, 4))
		
		pygame.display.flip()
		end = time.time()
		
		diff = end - start
		delay = 1.0 / fps - diff
		if delay > 0:
			time.sleep(delay)
		else:
			last_fps = 1.0 / diff
			
		scene = scene.next
