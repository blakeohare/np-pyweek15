import time
import pygame
from src.images import get_image
from src import worldmap
from src.font import get_text
from src import util
from src import network

class Element:
	def __init__(self, type, x, y):
		self.type = type
		self.x = x
		self.y = y
		self.focusable = True
		self.enabled = True
	
	def render(self, screen, is_focused):
		pass
	
	def enable(self):
		self.enabled = True
		self.focusable = True
		
	def disable(self, scene=None):
		if self.enabled:
			self.enabled = False
			self.focusable = False
			if scene != None and scene.get_focused_item() == self:
				scene.cycle_focus(1)

class Image(Element):
	def __init__(self, x, y, path):
		Element.__init__(self, "Image", x, y)
		self.img = get_image(path)
		self.focusable = False
		self.width = self.img.get_width()
		self.height = self.img.get_height()
	
	def render(self, screen, is_focused):
		screen.blit(self.img, (self.x, self.y))

class TextBox(Element):
	def __init__(self, x, y, width, watermark='', starting_text=''):
		Element.__init__(self, "TextBox", x, y)
		self.width = width
		self.height = 18
		self.box = pygame.Rect(self.x, self.y, self.width, self.height)
		self.counter = 0
		self.text = starting_text
		self.watermark = watermark
	
	def render(self, screen, is_focused):
		self.counter += 1
		pygame.draw.rect(screen, (0,0, 0), self.box)
		pygame.draw.rect(screen, (0, 128, 255), self.box, 1)
		
		text = self.text
		color = (255, 255, 255)
		farleft = False
		if len(self.text) == 0:
			text = self.watermark
			color = (80, 80, 80)
			farleft = True
		
		t = get_text(text, color, 16)
		screen.blit(t, (self.x + 2, self.y + 4))
		if is_focused and (self.counter // 10) % 2 == 0:
			x = self.x + 2
			if not farleft:
				x += t.get_width()
			pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(x, self.y + 3, 1, 12))
		

class UiScene:
	def __init__(self):
		self.next = self
		self.elements = []
		self.focused_item = -1
		self.initialized = False
		self.captured = None
	
	def initialize(self):
		self.cycle_focus(1)
	
	def cycle_focus(self, direction):
		if len(self.elements) == 0:
			return
		for i in range(len(self.elements)):
			index = (self.focused_item + (i + 1) * direction) % len(self.elements)
			if self.elements[index].focusable:
				self.focused_item = index
				return
		self.focused_item = -1
	
	def get_focused_item(self):
		if self.focused_item < 0: return None
		return self.elements[self.focused_item]
	
	def add_element(self, element):
		self.elements.append(element)
	
	def hit_test(self, item, x, y):
		if not item.focusable: return False
		if x < item.x: return False
		if y < item.y: return False
		if x > item.x + item.width: return False
		if y > item.y + item.height: return False
		return True
	
	def process_input(self, events, pressed_keys):
		if not self.initialized:
			self.initialize()
			self.initialized = True
		
		focused = self.get_focused_item()
		for event in events:
			if event.type == 'mouseleft':
				px = event.x
				py = event.y
				if event.down:
					i = len(self.elements) - 1
					while i >= 0:
						item = self.elements[i]
						r = item.x + item.width
						b = item.y + item.height
						if self.hit_test(item, px, py):
							self.focused_item = i
							self.captured = item
							break
						i -= 1
				else:
					if self.captured != None:
						if self.captured.type == "Button":
							if self.hit_test(self.captured, px, py):
								self.captured.handler()
							
			elif focused != None:
				if focused.type == "TextBox":
					if event.type == 'type':
						key = event.action
						if key == 'bs':
							focused.text = focused.text[:-1]
						elif key == 'tab':
							self.cycle_focus(1)
						elif key == 'TAB':
							self.cycle_focus(-1)
						else:
							focused.text += key
	
	def update(self):
		pass
	
	def render(self, screen):
		focused = self.get_focused_item()
		for element in self.elements:
			element.render(screen, focused == element)

class Button(Element):
	def __init__(self, x, y, label, handler, enabled):
		Element.__init__(self, "Button", x, y)
		self.text = label
		self.handler = handler
		self.width = get_text(label, (255, 255, 255), 18).get_width() + 4
		self.height = 18
		if enabled:
			self.enable()
		else:
			self.disable(None)
	
	def render(self, screen, is_focused):
		box = pygame.Rect(self.x, self.y, self.width, self.height)
		color = (255, 255, 255) if self.enabled else (128, 128, 128)
		pygame.draw.rect(screen, (40, 40, 40), box)
		pygame.draw.rect(screen, color, box, 1)
		img = get_text(self.text, color, 18)
		screen.blit(img, (self.x + 2, self.y + 2))

class TitleScene(UiScene):
	def __init__(self):
		UiScene.__init__(self)
		self.username = TextBox(20, 200, 100, "Username")
		self.add_element(Image(0, 0, 'title.png'))
		self.add_element(self.username)
		self.button = Button(20, 230, "Login", self.login_pressed, False)
		self.add_element(self.button)
		self.auth_request = None
	
	def update(self):
		UiScene.update(self)
		if len(self.username.text) == 0:
			self.button.disable()
		else:
			self.button.enable()
		
		if self.auth_request != None and self.auth_request.has_response():
			print "Got the following response:", self.auth_request.response, self.auth_request.get_response()
			self.auth_request = None
		worldmap.killtime(0.05)
	
	def login_pressed(self):
		raw_users = util.read_file('users.txt')
		if raw_users == None:
			users = []
		else:
			users = util.trim(raw_users).split('\n')
		user_lookup = {}
		for user in users:
			name = util.trim(user[32:])
			password = user[:32].lower()
			user_lookup[name] = password
		
		user = self.username.text
		password = user_lookup.get(user, None)
		if password == None:
			password = util.md5(str(time.time()) + "leprechauns")
			raw_users += "\n" + password + user
			util.write_file('users.txt', raw_users)
		self.auth_request = network.send_authenticate(user, password)
	
	def process_input(self, events, pressed_keys):
		if pressed_keys['debug']:
			self.next = worldmap.WorldViewScene()
		UiScene.process_input(self, events, pressed_keys)
	
