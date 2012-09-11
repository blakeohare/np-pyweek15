import pygame, math
from src import worldmap, camera, settings, terrain

class Sprite(object):
	def __init__(self, x, y, z=None):
		self.x, self.y = terrain.toRender(x, y)
		self.z = terrain.height(self.x, self.y) if z is None else z

	def lookatme(self):
		camera.lookat(self.x, self.y, terrain.height(self.x, self.y))

	def trackme(self):
		camera.track(self.x, self.y, terrain.height(self.x, self.y), settings.trackvalue)

	def rendershadow(self, screen):
		px, py = camera.screenpos(self.x, self.y, terrain.height(self.x, self.y))
		pygame.draw.ellipse(screen, (0, 0, 0), (px-4, py-2, 8, 4))

	def update(self):
		pass

	def getModelXY(self):
		return terrain.toModel(self.x, self.y)

	def setModelXY(self, x, y):
		self.x, self.y = terrain.toRender(self.x, self.y)

	def drawmini(self, surf, x0, y0):
		px, py = int((self.x - x0)//1), int((-self.y + y0)//1)
		pygame.draw.line(surf, self.minicolor, (px-1,py), (px+1,py))
		pygame.draw.line(surf, self.minicolor, (px,py-1), (px,py+1))

# Just a bouncing ball for now
class You(Sprite):
	v = 0.4  # tiles per frame
	minicolor = 255, 0, 0  # color on the minimap

	def move(self, dx, dy):
		self.x += dx * self.v
		self.y += dy * self.v

	def update(self):
		import time
		self.z = terrain.height(self.x, self.y) + int(abs(5 * math.sin(7 * time.time())))

	def render(self, screen):
		self.rendershadow(screen)
		px, py = camera.screenpos(self.x, self.y, self.z)
		pygame.draw.circle(screen, (255, 0, 0), (px, py-4), 4)

