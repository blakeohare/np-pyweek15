import pygame
import time
import os
from collections import defaultdict

import menus, worldmap

# types: key, type, mouseleft, mouseright, mousemove
# action: left, right, up down, build, enter, demolish
event_actions = 'left, right, up down, build, enter, demolish'.split(', ')
class MyEvent:
	def __init__(self, type, action, down, x, y):
		self.type = type
		self.action = action
		self.down = down
		self.up = not down
		self.x = x
		self.y = y

full_screen_mode = True

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
				
				# TODO: typing events
				# TODO: mouse events
				# TODO: full screen event
		
		
		scene.process_input(events, pressed_keys)
		scene.update()
		scene.render(vscreen)
		
		pygame.transform.scale(vscreen, rscreen.get_size(), rscreen)
		
		pygame.display.flip()
		end = time.time()
		
		diff = end - start
		delay = 1.0 / fps - diff
		if delay > 0:
			time.sleep(delay)
		
		scene = scene.next
