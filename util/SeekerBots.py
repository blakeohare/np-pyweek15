import Image
import pygame
import os

pygame.init()
pygame.display.set_mode((400, 300))

directory = '..' + os.sep + 'images'
full_path = directory + os.sep + 'seekerbot.png'
#target_path = os.path.join(directory, '@@@', building)
image = Image.open(full_path)
print image.mode, full_path
if image.mode != 'RGBA':
	surf = pygame.image.load(full_path).convert_alpha()
	pygame.image.save(surf, full_path)
	image = Image.open(full_path)
	print "reimaged to", image.mode

for changeTo in ['purple', 'blue', 'green']:
	
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
			
			if b > r:
				if changeTo == 'purple':
					r,b = b, b
					r = r
					#b = b * 2 / 3
					r = r * 2 / 3
					g = g * 2 / 3
					b = b * 2 / 3
					
				elif changeTo == 'green':
					g, b = b, g
					r = r * 2 / 3
					g = g * 2 / 3
					b = b * 2 / 7
			
			pixels[x, y] = (r, g, b, a)
			
			x += 1
		y += 1
	target_path = full_path.replace('seekerbot', 'seekerbot_' + changeTo)
	image.save(target_path)
