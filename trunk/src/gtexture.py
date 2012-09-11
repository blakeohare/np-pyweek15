# ground texture
import pygame
from src import terrain, settings

# water colors light to dark
ws = (20,20,200), (10,10,170), (0,0,140), (0,0,110), (0,0,70)

# lowland colors yellow to brown to green
ls = (100,100,0), (90,80,0), (80,40,0), (80,70,0), (50,80,0), (40,90,0)

# highland colors green to gray to white
hs = (40,90,0), (50,100,10), (60,80,30), (70,70,70), (85,85,85), (100,100,100)

grads = {
	0: (ws[0],),
	-1: (ws[0], ws[1]),
	-2: (ws[0], ws[1], ws[1]),
	-3: (ws[1], ws[0]),
	-4: (ws[1], ws[2]),
	-5: (ws[1], ws[2], ws[2]),
	-6: (ws[2], ws[1]),
	-7: (ws[2], ws[3]),
	-8: (ws[2], ws[3], ws[3]),
	-9: (ws[3], ws[2]),
	-1000: (ws[3],),
	
	1: (ls[0], ls[1]),
	2: (ls[0], ls[1], ls[1]),
	3: (ls[1], ls[0],),
	4: (ls[1], ls[2],),
	5: (ls[1], ls[2], ls[2]),
	6: (ls[2], ls[1],),
	7: (ls[2], ls[3],),
	8: (ls[2], ls[3], ls[3]),
	9: (ls[3], ls[2],),
	10: (ls[3], ls[4],),
	11: (ls[3], ls[4], ls[4]),
	12: (ls[4], ls[3],),
	10: (ls[4], ls[5],),
	11: (ls[4], ls[5], ls[5]),
	12: (ls[5], ls[4],),

	13: (hs[0], hs[1]),
	14: (hs[0], hs[1], hs[1]),
	15: (hs[1], hs[0],),
	16: (hs[1], hs[2],),
	17: (hs[1], hs[2], hs[2]),
	18: (hs[2], hs[1],),
	19: (hs[2], hs[3],),
	20: (hs[2], hs[3], hs[3]),
	21: (hs[3], hs[2],),
	22: (hs[3], hs[4],),
	23: (hs[3], hs[4], hs[4]),
	24: (hs[4], hs[3],),
	25: (hs[4], hs[5],),
	26: (hs[4], hs[5], hs[5]),
	27: (hs[5], hs[4],),
	28: (hs[5],),
}

iw0, ih0 = 40, 60
textures = {}
def fillwithgrad(s, grad):
	s.fill(grad[0])
	if len(grad) == 1: return
	for y in range(0,ih0,2):
		for x in range(0,iw0,2):
			if len(grad) > 1:
				s.set_at((x,y), grad[1])
			if len(grad) > 2:
				s.set_at((x+1,y+1), grad[2])
			if len(grad) > 3:
				s.set_at((x,y+1), grad[3])
		
def texture(h0, g):
	if h0 <= 0: g = 0
	if (h0, g) not in textures:
		s = pygame.Surface((iw0, ih0)).convert()
		a = 1.0 + 0.04 * (g-10)
		grad = [[int(a*x) for x in c] for c in
			grads[max(a for a in grads if a <= h0)]]
		fillwithgrad(s, grad)
		textures[(h0, g)] = s
	return textures[(h0, g)]


def putterrain(surf, h, h0, g, ps):
	g = int(g//0.1)
	g = -10 if g < -10 else 10 if g > 10 else g
	if h > 0: h0 = max(h0, 1)
#	if not settings.usetgradient or h <= 0:
#		return pygame.draw.polygon(surf, hcolor(h, g, 0), ps)
#	tgrad = images.get_image("terrain-gradient.png")
	xs, ys = zip(*ps)
	x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
	xs = [x-x0 for x in xs]
	ys = [y-y0 for y in ys]
	w, h = x1-x0+1, y1-y0+1
	s = pygame.Surface((w, h)).convert()
	mask = pygame.Surface((w, h)).convert()
	mask.fill((255,0,255))
	mask.set_colorkey((0,0,0))
	pygame.draw.polygon(mask, (0,0,0), [(x-x0,y-y0) for x,y in ps])
	s.blit(texture(h0, g), (x0%2,y0%2))
	s.blit(mask, (0,0))
	s.set_colorkey((255,0,255))
	surf.blit(s, (x0, y0))

def hcolor(h, h0, g):
	if h > 0: h0 = max(h0, 1)
	g = g / 0.1 if h0 > 0 else 0
	c = grads[max(a for a in grads if a <= h0)][0]
	f = min(max(1.0 + 0.04 * (g-10), 0), 1)
	return [int(f*x) for x in c]

