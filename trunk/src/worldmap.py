import random
from collections import defaultdict

noiseseed = "one way trip"
nmapsize = 64

tf0 = 0.03
tfactors = 1.000, 1.618, 2.618, 4.236, 6.854, 11.090, 17.944, 29.034
sealevel = -0.3
tscale = 40

parcelsize = 40


# seed the RNG for reproducible noise map
try:
    random.seed(noiseseed, version = 1)
except TypeError:
    random.seed(noiseseed)
r = random.randint(0, 99999999)
assert r == 99082844, "Something wrong with the random number generation. Aborting!"
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
def height0(x, y):
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

# This is a set of cached values to speed up height calculations - don't worry about it.
dpcache, dpmin, dpmax = {}, 0, 0
def setdp(xx):
    xs = [xx*f*tf0 % nmapsize for f in tfactors]
    dpcache[xx] = [(int(x), x - int(x)) for x in xs]
setdp(0)
def dpextend(x0, x1):
    global dpmin, dpmax
    while dpmin > x0:
        dpmin -= 1
        setdp(dpmin)
    while dpmax < x1:
        dpmax += 1
        setdp(dpmax)

class Parcel(object):
    def __init__(self, x0, y0):
        self.x0, self.y0 = x0, y0
        self.h = {}
        self.ready = False

    def compute(self):
        dpextend(min(self.x0, self.y0) - 4, max(self.x0, self.y0) + parcelsize + 4)
        yield
        # Determine heights for corners
        for y in range(self.y0 - 2, self.y0 + parcelsize + 3):
            for x in range(self.x0 - 2 + y % 2, self.x0 + parcelsize + 3, 2):
                # TODO: easy integer map to actual h values
                h = -sealevel
                for f, (xx, tx), (yy, ty) in zip(tfactors, dpcache[x], dpcache[y]):
                    h += ((noisemap[xx][yy] * (1-tx) + noisemap[xx+1][yy] * tx) * (1-ty) + 
                        (noisemap[xx][yy+1] * (1-tx) + noisemap[xx+1][yy+1] * tx) * ty)
                h *= tscale
                if h > 0: h -= min(h/2, 20)
                self.h[(x, y)] = int(h)
            yield
        self.hcorners = {}
        self.hcmax = {}
        # Determine heights for tiles
        for y in range(self.y0 - 1, self.y0 + parcelsize + 2):
            for x in range(self.x0 - 1 + y % 2, self.x0 + parcelsize + 2, 2):
                hs = self.h[(x-1,y)], self.h[(x,y-1)], self.h[(x+1,y)], self.h[(x,y+1)]
                self.hcorners[(x,y)] = hs
                self.hcmax[(x,y)] = max(hs)
                self.h[(x,y)] = sum(hs)/4
            yield
        self.ready = True

    def getheight(self, x, y):
        if not self.ready:
            for _ in self.compute():
                pass
        X, Y = (x + y) / 2, (-x + y) / 2
        iX, iY = int(X), int(Y)
        ix, iy = iX - iY, iX + iY
        tX, tY = X - iX, Y - iY
        return ((self.h[(ix,iy)] * (1-tX) + self.h[(ix+1,iy+1)] * tX) * (1-tY) + 
                (self.h[(ix-1,iy-1)] * (1-tX) + self.h[(ix,iy+2)] * tX) * tY)


class parceldict(defaultdict):
    def __missing__(self, key):
        x, y = key
        ret = self[key] = Parcel(x*parcelsize, y*parcelsize)
        return ret
parcels = parceldict()
def height(x, y):
    return parcels[(int(x//parcelsize), int(y//parcelsize))].getheight(x, y)

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


