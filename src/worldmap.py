import random

noiseseed = "one way trip"
nmapsize = 64

tf0 = 0.03
tfactors = 1.000, 1.618, 2.618, 4.236, 6.854, 11.090, 17.944, 29.034
sealevel = -0.3
tscale = 40


# seed the RNG for reproducible noise map
try:
    random.seed(noiseseed, version = 1)
except TypeError:
    random.seed(noiseseed)
assert random.randint(0, 99999999) == 99082844, \
    "Something wrong with the random number generation. Aborting!"
# Generate the noise map to be used for all terrain
noisemap = [[random.uniform(-1, 1) for x in range(nmapsize)]
               for y in range(nmapsize)]
noisemap = [row + row[0:1] for row in noisemap]
noisemap += noisemap[0:1]

# Reference implementation - slow
def noisevalue(x, y):
    x %= nmapsize
    y %= nmapsize
    tx, ty = x - int(x), y - int(y)
    x, y = int(x), int(y)
    return ((noisemap[x][y] * (1-tx) + noisemap[x+1][y] * tx) * (1-ty) + 
            (noisemap[x][y+1] * (1-tx) + noisemap[x+1][y+1] * tx) * ty)

# Reference implementation - slow
def height(x, y):
    h = -sealevel
    for f in tfactors:
        h += noisevalue(x*f*tf0, y*f*tf0) / f
    h *= tscale
    if h > 0: h -= min(h/2, 20)
    return int(h)

def hcolor(h):
    if h < 0: return (0,0,100)
    if h < 4: return (160,160,80)
    if h < 16: return (90,90,0)
    if h < 25: return (100,50,0)
    if h < 40: return (100,100,100)
    return (140,140,140)

if __name__ == "__main__":
    import pygame
    from pygame import *
    screen = display.set_mode((800, 600))
    display.set_caption("Don't worry, the real game will be much faster at this.")
    for y in range(600):
        for x in range(800):
            h = height(x, y)
            c = hcolor(h)
            screen.set_at((x, y), c)
        draw.rect(screen, (255, 255, 255), (100, 100, 20, 30), 1)
        pygame.display.flip()
        if any(event.type in (KEYDOWN, QUIT) for event in pygame.event.get()):
            exit()
    while not any(event.type in (KEYDOWN, QUIT) for event in pygame.event.get()):
        pass
    image.save(screen, "map-example.png")


