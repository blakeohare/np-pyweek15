import pygame
import os

_images = {}

def get_image(path):
	img = _images.get(path)
	if img == None:
		rpath = ('images/' + path).replace('/', os.sep).replace('\\', os.sep)
		img = pygame.image.load(rpath)
		_images[path] = img
	return img


def spritesheet(path, nx, ny):
	sheet = get_image(path)
	r = {}
	w, h = sheet.get_width() // nx, sheet.get_height() // ny
	for x in range(nx):
		for y in range(ny):
			s = pygame.Surface((w, h)).convert_alpha()
			s.fill((0,0,0,0))
			s.blit(sheet, (-w*x, -h*y))
			r[(x,y)] = s
	return r

