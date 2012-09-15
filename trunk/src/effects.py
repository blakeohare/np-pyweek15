# A list of special effects that don't affect the gameplay.
# It's really easier to just give in and make this a singleton, rather than passing around a list
#   everywhere that any entity can append to.

# Effects should have an alive attribute, an update method, and a render method
# They need to at least have a y-coordinate, for drawing order.
# Effects are not rendered on the minimap

import pygame, random, math
from src import camera, jukebox, images

effects = []

def update():
	global effects
	for e in effects:
		e.update()
	effects = [e for e in effects if e.alive]

def add(e):
	if e.sound: jukebox.play_sound(e.sound)
	effects.append(e)

class Gunshot(object):
	color = 24,24,24
	lifetime = 2
	width = 2
	sound = "gunshot"
	def __init__(self, x0, y0, z0, x1, y1, z1):
		self.x0, self.y0, self.z0 = x0, y0, z0
		self.x1, self.y1, self.z1 = x1, y1, z1
		self.y = (self.y0 + self.y1) / 2.
		self.t = 0
		self.alive = True
	def update(self):
		self.t += 1
		self.alive = self.t <= self.lifetime
	def render(self, screen, looker=None):
		looker = looker or camera
		p0 = looker.screenpos(self.x0, self.y0, self.z0)
		p1 = looker.screenpos(self.x1, self.y1, self.z1)
		pygame.draw.line(screen, self.color, p0, p1, self.width)

class LaserBeam(Gunshot):
	color = 255,255,128
	lifetime = 4
	width = 2
	sound = "beamish"

class BotBeam(Gunshot):
	color = 255,0,0
	lifetime = 2
	width = 1
	sound = "beamish"

class LightningBolt(object):
	color0 = 200,200,255
	color1 = 100,100,255
	lifetime = 6
	sound = "zap"
	def __init__(self, x0, y0, z0, x1, y1, z1, r):
		self.x0, self.y0, self.z0 = x0, y0, z0
		self.x1, self.y1, self.z1 = x1, y1, z1
		self.r = r
		self.y = self.y1
		self.t = 0
		self.alive = True
	def update(self):
		self.t += 1
		self.alive = self.t <= self.lifetime
	def render(self, screen, looker=None):
		looker = looker or camera
		x0,y0 = looker.screenpos(self.x0, self.y0, self.z0)
		x1,y1 = looker.screenpos(self.x1, self.y1, self.z1)
		for _ in range(2):
			ps = [(int(x0*f+x1*(1-f)+random.random()*20-10),
				   int(y0*f+y1*(1-f)+random.random()*20-10))
				   for f in (0.75, 0.5, 0.25)]
			pygame.draw.lines(screen, self.color0, False, [(x0,y0)] + ps + [(x1,y1)], 2)

		for _ in range(4):
			theta = random.random() * 1000
			x0,y0 = looker.screenpos(self.x1+self.r*math.sin(theta), self.y1+self.r*math.cos(theta), self.z1)
			ps = [(int(x0*f+x1*(1-f)+random.random()*20-10),
				   int(y0*f+y1*(1-f)+random.random()*20-10))
				   for f in (0.75, 0.5, 0.25)]
			pygame.draw.lines(screen, self.color1, False, [(x0,y0)] + ps + [(x1,y1)], 1)


class Spark(object):
	color = 255,128,255
	v = 1.0
	sound = None
	def __init__(self, x0, y0, z0, x1, y1, z1):
		self.x0, self.y0, self.z0 = x0, y0, z0
#		self.x1, self.y1, self.z1 = x1, y1, z1
		self.x, self.y, self.z = x0, y0, z0
		self.dx, self.dy, self.dz = x1-x0, y1-y0, z1-z0
		self.d = math.sqrt(self.dx**2 + self.dy**2)
		self.t, self.p = 0, -self.v
		self.alive = True
	def update(self):
		self.t += 1
		self.p += self.v
		self.alive = self.p < self.d
	def render(self, screen, looker=None):
		looker = looker or camera
		for dp in (0.,0.4,0.8):
			f = (self.p + dp) / self.d
			if f > 1 or f < 0: continue
			h = f*(1-f)*150
			p1 = looker.screenpos(self.x0+self.dx*f, self.y0+self.dy*f, self.z0+self.dz*f+h)
			pygame.draw.circle(screen, self.color, p1, 3, 1)

class Tractor(object):
	color = 255,0,128
	width = 4
	sound = "phaser"
	def __init__(self, source, target):
		self.source = source
		self.target = target
		self.t = 0
		self.alive = True
	def update(self):
		self.y = (self.source.y + self.target.y) / 2.
		if self.target not in self.source.targets:
			self.alive = False
	def render(self, screen, looker=None):
		looker = looker or camera
		p0 = looker.screenpos(self.source.x, self.source.y, self.source.z + self.source.h)
		p1 = looker.screenpos(self.target.x, self.target.y, self.target.z + 2)
		pygame.draw.line(screen, self.color, p0, p1, self.width)


class Splat(object):
	sound = None
	lifetime = 9
	def __init__(self, x, y, z):
		self.x, self.y, self.z = x, y, z
		self.t = 0
		self.alive = True
	def update(self):
		self.t += 1
		if self.t >= self.lifetime:
			self.alive = False
	def render(self, screen, looker=None):
		looker = looker or camera
		f = self.t * 1. / self.lifetime
		h = f * (1-f) * 40
		s = int(4 + 10 * f)
		img = pygame.transform.scale(images.get_image("effects/alienblood.png"), (2*s, s))
		x, y = looker.screenpos(self.x, self.y, self.z + h)
		screen.blit(img, (x-s, y-s//2))

class Smoke(object):
	sound = None
	lifetime = 4
	def __init__(self, x, y, z, vx, vy, vz):
		self.x, self.y, self.z = x, y, z
		self.vx, self.vy, self.vz = vx, vy, vz
		self.t = 0
		self.alive = True
	def update(self):
		self.t += 1
		if self.t >= self.lifetime:
			self.alive = False
		self.x += self.vx
		self.y += self.vy
		self.z += self.vz
	def render(self, screen, looker=None):
		looker = looker or camera
		f = 1. * self.t / self.lifetime
		alpha = max(int(255 - 200 * f), 0)
		img = images.get_image("effects/boom.png")
		img.set_alpha(alpha)
		x, y = looker.screenpos(self.x, self.y, self.z)
		screen.blit(img, (x-5, y-5))

class SmokeCloud(object):
	sound = None
	lifetime = 7
	def __init__(self, x, y, z):
		self.x, self.y, self.z = x, y, z
		self.t = 0
		self.alive = True
	def update(self):
		self.t += 1
		if self.t >= self.lifetime:
			self.alive = False
		for _ in range(4):
			vx, vy, vz = random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 0.4
			add(Smoke(self.x, self.y, self.z, vx, vy, vz))
	def render(self, screen, looker=None):
		pass


