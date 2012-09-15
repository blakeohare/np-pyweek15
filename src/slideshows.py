import pygame
from src import scenefactory, util
from src.images import get_image
from src.font import get_text
from src import jukebox

page1 = util.trim("""
They say that in these enlightened times, society has
evolved beyond the need for barbaric customs of 
punishing crime. Long gone are the stocks, the electric
chair, and the prison cell; instead, those who inflict
pain or suffering on others are gently removed and
placed on a lush deserted planet where they are given
the freedom to live peaceful, fulfilling lives in a
community of equals.
""").split('\n')

page2 = util.trim("""
However, they are wrong.
""").split('\n')

page3 = util.trim("""
In truth, not just criminals but anyone who disagrees
with the ruling government is forever exiled to this
remote prison planet. Life on this prison planet is
brutal; it's difficult to scrape out a living when
some of your neighbors are petty thieves and killers,
and the knowledge that no one has ever escaped only
makes existence that much harder.
""").split('\n')

page4 = util.trim("""
Of course, if all this weren't bad enough, there are
whispers among the exiles that the planet might not
be quite as deserted as they were told. Prisoners are
disappearing, buildings are being destroyed, and there
are disturbing signs that they might not be alone on
this world, and the new neighbors aren't very friendly.
""").split('\n')

page5 = util.trim("""
You're about to find all of this out for yourself, as
the transport ship you are on descends to the planet's
surface, and your sentence is carried out. You're going
to have to learn to survive on this barren world, by
taming the land, taking advantage of your neighbors'
prosperity, and coping with the mysterious threat. It's
going to take a lot of hard work and fast thinking, but
maybe, just maybe, eventually you'll even find a way to
get back home.
""").split('\n')

pages = [page1, page2, page3, page4, page5]

class StoryScene:
	def __init__(self):
		self.next = self
		self.images = [
			get_image('backgrounds/story1.png'),
			None,
			get_image('backgrounds/story2.png'),
			get_image('backgrounds/story2.png'),
			get_image('backgrounds/story3.png')]
		
		self.pos = [
			(10, 10),
			(10, 10),
			(50, 140),
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
		jukebox.ensure_playing('intro')
	
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
			t = get_text(line, (255, 255, 255), 18, (0, 0, 0))
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
		jukebox.ensure_playing('credits')
	
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
	

class EndingScene:
	def __init__(self):
		self.next = self
		self.pages = [
			get_image('backgrounds/ending1.png'),
			get_image('backgrounds/ending1.png'),
			get_image('backgrounds/ending1.png'),
			get_image('backgrounds/ending1.png'),
			get_image('backgrounds/ending2.png'),
			get_image('backgrounds/ending2.png')]
		self.text = [
		util.trim("""
			Despite the fact that you can still see hordes of the
			alien monsters on the horizon, you begin the launch
			sequence for your homemade spaceship, hoping for the best.
			Amazingly enough, the patchwork rocket engine ignites.
			The hastily constructed frame groans as the fuel burns;
			this is a one-way trip, so you better hope your""").split('\n'),
			
		util.trim("""
			destination isn't too far. You've used the computer to
			calculate where your home world is, hoping you'll be able
			to hide among your family and friends, counting on the fact
			that no one has escaped the prison planet before to mean
			they won't be looking for you. It's a desperate gamble, but
			it's better than being trapped for the rest of your life.
		""").split('\n'),

			util.trim("""
				You're not sure how long you spend traveling through
				the blackness of space, but finally you think you
				have arrived at the location the computer indicated
				your home would be. It's not a moment too soon; your
				fuel supply is nearly depleted. You buckle in and
				start the landing sequence; hoping to survive.""").split('\n'),
				
				util.trim("""

			Your arrival was more on the "crash" side of landing,
			but you're in one piece! You open the hatch to your rocket,
			ready to make your way home.""").split('\n'),
			
			util.trim("""
				Except something is wrong; where are the houses,
				the architecture, the parks and fountains? Even
				in the most uninhabited areas, it didn't look
				like this: barren, almost lifeless. You cautiously
				approach the small crowd gathered around your craft;
				they're a motley bunch, looking shifty and suspicious. """).split('\n'),
				
				util.trim("""
			"Where am I? Isn't this Earth?"
			
			They look at each other, and an older man with one eye
			and a lot of tattoos answers, "Sure was, stranger, but
			it ain't much of anythin' no more."
			
			"What do you mean? This is my home!"
			
			"Ain't no one's home; they moved the locals out of here
			when they made this a prison planet. You must be crazy
			to come here, cause everyone knows there ain't no way out!"
		""").split('\n')
		
		]
		self.current = 0
		self.counter = 0
	def process_input(self, events, pressed):
		for event in events:
			if event.type == 'key':
				if event.down:
					if event.action in ('build', 'action', 'shoot', 'back'):
						self.current += 1
		
		if self.current == len(self.text):
			self.current -= 1
			from src import title
			self.next = CreditsScene(False)
	
	def update(self):
		self.counter += 1
	
	def render(self, screen):
		screen.blit(self.pages[self.current], (0, 0))
		y = 20
		x = 10
		for line in self.text[self.current]:
			img = get_text(util.trim(line), (0, 0, 0), 18)
			screen.blit(img, (x, y))
			y += img.get_height() + 4
	
scenefactory.add_builder('story', lambda:StoryScene())
scenefactory.add_builder('credits', lambda x:CreditsScene(x))
