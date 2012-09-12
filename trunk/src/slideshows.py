import pygame
from src import scenefactory, util
from src.images import get_image
from src.font import get_text

page1 = util.trim("""
They say that in these enlightened times, society has
evolved beyond the need for the old barbaric customs
of punishing crime. Long gone are the stocks, the 
electric chair, and the prison cell; instead, those
who inflict pain or suffering on others are gently
removed from whatever external factors have caused
their distress.
""").split('\n')

page2 = util.trim("""
They are placed on a deserted, lush planet in another
solar system, where they are given the freedom to 
live peaceful, fulfilling lives without any penalties
or reproach for their actions in a community of equals.
""").split('\n')

page3 = util.trim("""
Of course, "they" are wrong.
""").split('\n')

page4 = util.trim("""
In truth, you've been exiled to a planet on which you're
just scraping by, trying to stay alive; a planet which
is populated by other prisoners ranging from petty
thieves to killers; and a planet that might not be quite
as deserted as you've been led to believe. Strange things
have been happening to folks around you, and there are
signs that there might be life other than you around.

""").split('\n')

page5 = util.trim("""
Unfortunately, those signs include burned out buildings
and the odd disappearance, so that life might not be any
friendlier than your fellow outcasts. Maybe someday you'll
be able to escape this place, but right now you'd better
figure out how to survive first.
""").split('\n')

pages = [page1, page2, page3, page4, page5]

class StoryScene:
	def __init__(self):
		self.next = self
		self.images = [
			get_image('backgrounds/story1.png'),
			get_image('backgrounds/story2.png'),
			None,
			get_image('backgrounds/story3.png'),
			get_image('backgrounds/story4.png')]
		
		self.pos = [
			(10, 10),
			(10, 10),
			(120, 140),
			(10, 10),
			(10, 10)
		]
		self.page = 0
	
	def process_input(self, events, pressed):
		for event in events:
			
			if event.type == 'key' and event.down and event.action in ('action', 'back', 'build'):
				self.page += 1
		
		if self.page == len(self.images):
			self.page -= 1
			self.next = scenefactory.build_scene('title', [])
	
	def update(self):
		pass
	
	# TODO: fade transitions
	
	def render(self, screen):
		bg = self.images[self.page]
		if bg == None:
			screen.fill((0, 0, 0))
		else:
			screen.blit(bg, (0, 0))
		text = pages[self.page]
		y = self.pos[self.page][1]
		for line in text:
			t = get_text(line, (255, 255, 255), 18)
			screen.blit(t, (self.pos[self.page][0], y))
			y += t.get_height() + 6



		
	
class CreditsScene:
	def __init__(self, skippable=True):
		scenefactory.add_builder('story', lambda:CreditsScene())
		self.next = self
		self.skippable = skippable
		self.counter = 0
		self.credits = [
			["", "Credits", None, None],
			["Programming", "Blake O'Hare & Christopher Night", get_image('people/blake.png'), get_image('people/cosmo.png')],
			["Sprite & Building Art", "Angel McLaughlin", get_image('people/spears.png'), None],
			["Story & Title Art", "\"infinip\"", None, get_image('people/infinip.png')],
			["Music", "Adrian Cline", get_image('people/ikanreed.png'), None],
			["Writing & Voice", "Laura Freer", None, get_image('people/satyrane.png')]
		]
		
		i = 0
		while i < len(self.credits):
			img = self.credits[i][3]
			if img != None:
				self.credits[i][3] = pygame.transform.flip(img, True, False)
			i += 1
	
	def process_input(self, events, pressed):
		if self.skippable:
			if pressed['action'] or pressed['back'] or pressed['build']:
				self.next = scenefactory.build_scene('title', [])
	
	def update(self):
		self.counter += 1
	
	def render(self, screen):
		screen.fill((0, 0, 0))
		y = int(screen.get_height() - (self.counter - 1) * 1.5)
		sw = screen.get_width()
		for credit in self.credits:
			line1 = get_text(credit[0], (160, 160, 160), 16)
			line2 = get_text(credit[1], (255, 255, 255), 24)
			left1 = sw // 2 - line1.get_width() // 2
			left2 = sw // 2 - line2.get_width() // 2
			mleft = left1 if left1 < left2 else left2
			right1 = sw // 2 + line1.get_width() // 2
			right2 = sw // 2 + line2.get_width() // 2
			mright = right1 if right1 > right2 else right2
			screen.blit(line1, (left1, y))
			screen.blit(line2, (left2, y + line1.get_height() + 3))
			
			lperson = credit[2]
			rperson = credit[3]
			if lperson != None:
				screen.blit(lperson, (mleft - lperson.get_width() - 8, y - 8))
			if rperson != None:
				screen.blit(rperson, (mright + 8, y - 8))
			y += 220
		
		if y < 0:
			self.next = scenefactory.build_scene('title', [])
	
	
scenefactory.add_builder('story', lambda:StoryScene())
scenefactory.add_builder('credits', lambda x:CreditsScene(x))
