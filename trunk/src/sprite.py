import pygame, math, random
from src import worldmap, camera, settings, terrain
from src.images import get_image

class Sprite(object):
	hp0 = 1
	last_direction = 0
	def __init__(self, x, y, z=None):
		self.x, self.y = terrain.toCenterRender(x, y)
		self.z = terrain.height(self.x, self.y) if z is None else z
		self.alive = True
		self.hp = self.hp0

	def lookatme(self):
		camera.lookat(self.x, self.y, terrain.height(self.x, self.y))

	def trackme(self):
		camera.track(self.x, self.y, terrain.height(self.x, self.y), settings.trackvalue)

	def screenpos(self, looker=None):
		return (looker or camera).screenpos(self.x, self.y, self.z)

	# Stand this high above the ground at current position
	def setheight(self, h=0):
		self.z = terrain.height(self.x, self.y) + h

	def rendershadow(self, screen):
		px, py = camera.screenpos(self.x, self.y, terrain.height(self.x, self.y))
		pygame.draw.ellipse(screen, (20, 20, 20, 100), (px - 4, py - 2, 8, 4))

	def update(self):
		pass

	def getModelXY(self):
		return terrain.toModel(self.x, self.y)

	def setModelXY(self, x, y):
		self.x, self.y = terrain.toRender(self.x - .5, self.y - .5)

	def drawmini(self, surf, x0, y0):
		px, py = int((self.x - x0)//1), int((-self.y + y0)//1)
		pygame.draw.line(surf, self.minicolor, (px-1,py), (px+1,py))
		pygame.draw.line(surf, self.minicolor, (px,py-1), (px,py+1))

	# Probably won't be hurting the player character, but I'll put this here anyway.
	def hurt(self, dhp):
		self.hp = max(self.hp - dhp, 0)
		if self.hp <= 0:
			self.alive = False

	def move(self, dx, dy):
		self.vx = dx * self.v
		self.vy = dy * self.v
		self.moving = bool(dx or dy)
		if self.moving:
			a, b = (dx > 0) - (dx < 0), (dy > 0) - (dy < 0)
			self.last_direction = [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)].index((a,b))

	# pass it a function that returns whether a given tile is empty.
	def walk(self, isempty):
		nx = self.x + self.vx
		ny = self.y + self.vy
		if terrain.isunderwater(nx, ny):
			return False
		if isempty(self.x, self.y) and not isempty(nx, ny):
			return False
		self.x, self.y = nx, ny
		return True

little_yous = {}

class You(Sprite):
	v = 0.3   # tiles per frame
	minicolor = 255, 128, 0  # color on the minimap

	def __init__(self, x, y, z=None):
		Sprite.__init__(self, x, y, z)
		self.moving = False
		self.last_direction = 0
		self.counter = 0

	def update(self, scene):
		self.counter += 1
		self.walk(scene.empty_tile)
		self.setheight()

	def render(self, screen):
		if len(little_yous) == 0:
			sheet = get_image('playersprite.png')
			for direction in range(8):
				for y in range(4):
					yc = (0, 1, 0, 2)[y]
					img = pygame.Surface((11, 21)).convert_alpha()
					img.fill((0, 0, 0, 0))
					img.blit(sheet, (-11 * direction, -21 * yc))
					little_yous[(direction, y)] = img
		i = 0
		if self.moving:
			i = (self.counter // 3) % 4
		img = little_yous[(self.last_direction, i)]
		
		self.rendershadow(screen)
		px, py = self.screenpos()
		#pygame.draw.circle(screen, (255, 0, 0), (px, py-21), 4)
		screen.blit(img, (px - img.get_width() // 2, py - img.get_height()))

# Alien base class
class Alien(Sprite):
	walkspeed = 0.1
	runspeed = 0.2
	minicolor = 255, 255, 0
	size = 6
	attackrange = 1
	strength = 1

	def __init__(self, *args, **kw):
		Sprite.__init__(self, *args, **kw)
		self.target = None
		self.vx, self.vy = 0, 0

	def settarget(self, target):
		self.target = target

	def setpath(self, path):
		self.path = path

	def update(self, scene):
		self.vx, self.vy = 0, 0
		self.v = self.runspeed
		if self.target:
			dx, dy = self.target.x - self.x, self.target.y - self.y
			d = math.sqrt(dx**2 + dy**2)
			if d < self.attackrange:
				self.vx, self.vy = 0, 0
				self.attack(self.target)
				self.path = []

		if self.path:
			px, py = self.path[0]
			dx, dy = px - self.x, py - self.y
			d = math.sqrt(dx**2 + dy**2)
			print self.x, self.y, px, py, dx, dy, d, self.v
			if d <= self.v:
				self.x, self.y = px, py
				self.path.pop(0)
				if d:
					self.move(dx/d, dy/d)
			else:
				self.move(dx / d, dy / d)
				self.x += self.vx
				self.y += self.vy
#		self.walk(scene.empty_tile)
		self.setheight()

	def attack(self, target):
		self.target.hurt(self.strength)
		self.alive = False

	def drawmini(self, surf, x0, y0):
		px, py = int((self.x - x0)//1), int((-self.y + y0)//1)
		surf.set_at((px, py), self.minicolor)
	
	def render(self, screen, looker=None):
		self.rendershadow(screen)
		px, py = self.screenpos(looker)
		pygame.draw.circle(screen, self.minicolor, (px, py-self.size), self.size)



