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
	target_path = os.path.join(directory, '@@@', building)
	image = Image.open(full_path)
	print image.mode, building
	if image.mode != 'RGBA':
		surf = pygame.image.load(full_path).convert_alpha()
		pygame.image.save(surf, full_path)
		image = Image.open(full_path)
		print "reimaged to", image.mode

	for changeTo in (
		(0, 100, 255, 1, "selection"),
		(255, 0, 0, 1, "damage"),
		(None, None, None, 0.5, "disabled")):
			
		image = Image.open(full_path)
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
				
				
				if changeTo[3] == 1:
					r = r // 2 + changeTo[0] // 2
					g = g // 2 + changeTo[1] // 2
					b = b // 2 + changeTo[2] // 2
				else:
					a = a // 2
				
				pixels[x, y] = (r, g, b, a)
				
				x += 1
			y += 1
		
		image.save(target_path.replace('@@@', changeTo[4]))