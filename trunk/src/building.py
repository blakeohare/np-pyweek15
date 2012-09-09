import pygame
from src import worldmap, camera, images

class Building(object):
	# TODO: handle buildings with bigger footprints than 1x1
	def __init__(self, x, y, z=None):
		self.x, self.y = x, y
		self.z = worldmap.iheight(x, y) if z is None else z
    
	def renderplatform(self, screen):
		# TODO: this should probably be cached into an image
		x, y = self.x, self.y
		z0, z1, z2, z3 = worldmap.ihcorners(x, y)
		zm = max((z0, z1, z2, z3))
		p0,p1,p2,p3,p4,p5,p6 = [camera.screenpos(a,b,c) for a,b,c in
				((x-1,y,zm), (x,y-1,zm), (x+1,y,zm), (x,y+1,zm), (x-1,y,z0), (x,y-1,z1), (x+1,y,z2))]
		# left
		pygame.draw.polygon(screen, (0,100,100), (p0,p4,p5,p1))
		# right
		pygame.draw.polygon(screen, (0,50,50), (p1,p5,p6,p2))
		# top
		pygame.draw.polygon(screen, (0,70,70), (p0,p1,p2,p3))
    
	def render(self, screen):
		px, py = camera.screenpos(self.x, self.y, self.z)
		if not camera.isvisible(px, py, 100):
			return
		self.renderplatform(screen)
		img = images.get_image("buildings/%s.png" % self.btype)
		ix, iy = img.get_size()
		screen.blit(img, (px-ix//2, py-iy+ix//4))

	def update(self):
		pass

class HQ(Building):
	btype = "hq"

class Greenhouse(Building):
	btype = "greenhouse"

