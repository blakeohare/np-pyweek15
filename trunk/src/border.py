# A graphical border what wraps around yer base

import pygame
from src import camera, terrain

ccache = {}
def ctiles(r):
	if r in ccache: return ccache[r]
	a = int(r+0.999)
	c = [(x+y,x-y) for x in range(-a,a+1) for y in range(-a,a+1)
			if x**2+y**2 <= r**2]
	ccache[r] = c
	return ccache[r]

class Border(object):
	# Pass in a color and a sequence of (building, radius) pairs
	# Radii should be in model coordinates, but internally this class uses render coordinates
	def __init__(self, color, bradii):
		self.color = color
		self.tiles = set()
		for building, radius in bradii:
			x0, y0 = building.x, building.y + building.size - 1
			self.tiles |= set((x0 + dx, y0 + dy) for dx, dy in ctiles(radius))
		self.tiles = sorted(self.tiles)
		
		self.segs = []
		for x,y in self.tiles:
			ls = [((x+a,y+b),(x+c,y+d)) for a,b,c,d in
				[(0,1,-1,0),(0,1,1,0),(-1,0,0,-1),(1,0,0,-1)]]  # order kind of matters here so be careful
			for line in ls:
				if line in self.segs:
					self.segs.remove(line)
				else:
					self.segs.append(line)

		segs = set(self.segs)
		self.lines = []
		while segs:
			s0 = min(segs)
			segs.remove(s0)
			ps = [s0[0], s0[1]]
			found = True
			while found:
				tofind = ps[-1]
				found = False
				for p0,p1 in segs:
					if p0 == tofind:
						ps.append(p1)
						segs.remove((p0,p1))
						found = True
						break
					elif p1 == tofind:
						ps.append(p0)
						segs.remove((p0,p1))
						found = True
						break
			self.lines.append(ps)
		
		self.surfs = []
		for line in self.lines:
			ps = [camera.camera0.screenpos(x,y,terrain.iheight(x,y)) for x,y in line]
			xs, ys = zip(*ps)
			x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
			s = pygame.Surface((x1-x0+1,y1-y0+1)).convert_alpha()
			s.fill((0,0,0,0))
			pygame.draw.lines(s, self.color, False, [(x-x0,y-y0) for x,y in ps])
			self.surfs.append((x0,y0,s))
		
		self.xmin = min(x for x,y,s in self.surfs) - 10
		self.xmax = max(x+s.get_width() for x,y,s in self.surfs) + 10
		self.ymin = min(y for x,y,s in self.surfs) - 10
		self.ymax = max(y+s.get_height() for x,y,s in self.surfs) + 10

		self.tiles = set(self.tiles)

	def iswithin(self, x, y):
		return (x,y) in self.tiles

	def render(self, surf, looker = None):
		looker = looker or camera
		
		if not looker.rectvisible(self.xmin, self.ymin, self.xmax, self.ymax):
			return
		
		if looker is camera:
			for x, y, s in self.surfs:
				surf.blit(s, (x - camera.x0, y - camera.y0))
			return
		
		for line in self.lines:
			ps = [looker.screenpos(x,y,terrain.iheight(x,y)) for x,y in line]
			pygame.draw.lines(surf, self.color, False, ps)
		return

