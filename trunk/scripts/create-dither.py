import pygame, random, math

screen = pygame.display.set_mode((400, 400))

colors = [
    (0, (160, 160, 160)),
    (100, (80, 80, 80)),
    (200, (40, 100, 40)),
    (300, (160, 160, 40)),
    (400, (200,200,200)),
]




def k((y0, c)):
    z = (y-y0) / 100.
    return random.uniform(0, math.exp(-z**2))

for y in range(400):
    for x in range(400):
        c = max(colors, key = k)[1]
        a = x / 400.
        screen.set_at((x, y), [int(a*b) for b in c])
    pygame.display.flip()

pygame.image.save(screen, "images/terrain-gradient.png")

