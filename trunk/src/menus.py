from src.images import get_image
from src import worldmap

class TitleScene:
	def __init__(self):
		self.next = self
	
	def process_input(self, events, pressed_keys):
		if pressed_keys['build']:
			self.next = worldmap.WorldViewScene()
	
	def update(self):
		pass
	
	def render(self, screen):
		screen.blit(get_image('title.png'), (0, 0))
