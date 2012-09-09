from images import get_image

class TitleScene:
	def __init__(self):
		self.next = self
	
	def process_input(self, events, pressed_keys):
		pass
	
	def update(self):
		pass
	
	def render(self, screen):
		screen.blit(get_image('title.png'), (0, 0))