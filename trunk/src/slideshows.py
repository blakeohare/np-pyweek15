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
	
	def process_input(self, events, pressed):
		if pressed['action'] or pressed['back'] or pressed['build']:
			self.next = scenefactory.build_scene('title', [])
	
	def update(self):
		pass
	
	def render(self, screen):
		screen.fill((0, 0, 0))
	
	
scenefactory.add_builder('story', lambda:StoryScene())
scenefactory.add_builder('credits', lambda x:CreditsScene(x))
