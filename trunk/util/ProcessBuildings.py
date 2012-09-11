import Image
import pygame
import os

pygame.init()
pygame.display.set_mode((400, 300))

directory = os.path.join('..', 'images', 'buildings')
building_files = filter(
	lambda x: x.endswith('.png'),
	os.listdir(directory)
	)

for building in building_files:
	full_path = directory + os.sep + building
	target_path = os.path.join(directory, 'selection', building)
	image = Image.open(full_path)
	print image.mode, building
	if image.mode != 'RGBA':
		surf = pygame.image.load(full_path).convert_alpha()
		pygame.image.save(surf, full_path)
		image = Image.open(full_path)
		print "reimaged to", image.mode
	
	pixels = image.load()
	width = image.size[0]
	height = image.size[1]
	y = 0
	while y < height:
		x = 0
		while x < width:
			
			color = pixels[x, y]
			r = color[0]
			g = color[1]
			b = color[2]
			a = color[3]
			
			
			r = r // 2
			g = g // 2 + 50
			b = b // 2 + 127
			
			pixels[x, y] = (r, g, b, a)
			#print a
			x += 1
		y += 1
	
	image.save(target_path)