from src.menus import *

class BuildingMenu(UiScene):
	def __init__(self, playscene):
		UiScene.__init__(self)
		self.playscene = playscene
		bg = pygame.Surface((200, 180)).convert_alpha()
		bg.fill((0, 0, 0, 180))
		self.add_element(Image(100, 60, bg))
	
	
	def process_input(self, events, pressed):
		for event in events:
			if event.type == 'key':
				if event.action == 'back' or event.action == 'action':
					if event.down:
						self.next = self.playscene
						self.playscene.next = self.playscene
						break
	
	def update(self):
		UiScene.update(self)
		self.playscene.update()
	
	def render(self, screen):
		self.playscene.render(screen)
		UiScene.render(self, screen)
		# This won't be centered on full screen. 
		# Will need to pass in a 400x300 transparent image and then reblit in middle
		# I'll do that if people care deeply.
				
	