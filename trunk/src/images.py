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