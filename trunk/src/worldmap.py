import random, pygame
from collections import defaultdict
from src import camera

noiseseed = 2117066982  # hash("one way trip")
nmapsize = 64

tf0 = 0.03
tfactors = 1.000, 1.618, 2.618, 4.236, 6.854, 11.090, 17.944, 29.034
sealevel = -0.3
tscale = 30

parcelsize = 40


# seed the RNG for reproducible noise map
try:
    random.seed(noiseseed, version = 1)
except TypeError:
    random.seed(noiseseed)
assert random.random() == 0.9908284413950574, "Something wrong with the random number generation. Aborting!"
# Generate the noise map to be used for all terrain
noisemap = [[random.random() * 2 - 1 for x in range(nmapsize)]
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

def hcolor(h, gx, gy):
    a = 0.8 + 0.04 * gx
    if h <= 0: r = (0,0,100)
    elif h < 4: r = (160,160,80)
    elif h < 16: r = (90,90,0)
    elif h < 25: r = (100,50,0)
    elif h < 40: r = (100,100,100)
    else: r = (140,140,140)
    return [int(x*a) for x in r]

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
        self.ready = False

    def compute(self):
        dpextend(min(self.x0, self.y0) - 4, max(self.x0, self.y0) + parcelsize + 4)
        yield
        # Determine heights for corners
        self.h = {}
        for y in range(self.y0 - 2, self.y0 + parcelsize + 4):
            for x in range(self.x0 - 2 + (1 - y % 2), self.x0 + parcelsize + 5, 2):
                # TODO: easy integer map to actual h values
                h = -sealevel
                for f, (xx, tx), (yy, ty) in zip(tfactors, dpcache[x], dpcache[y]):
                    h += ((noisemap[xx][yy] * (1-tx) + noisemap[xx+1][yy] * tx) * (1-ty) + 
                        (noisemap[xx][yy+1] * (1-tx) + noisemap[xx+1][yy+1] * tx) * ty) / f
                h *= tscale
                if h > 0: h -= min(h/2, 20)
                self.h[(x, y)] = max(int(h), 0)
            yield
        self.hcorners = {}
        self.hcmax = {}
        self.grad = {}
        # Determine heights for tiles
        for y in range(self.y0 - 1, self.y0 + parcelsize + 3):
            for x in range(self.x0 - 1 + (1 - y % 2), self.x0 + parcelsize + 4, 2):
                hs = self.h[(x-1,y)], self.h[(x,y-1)], self.h[(x+1,y)], self.h[(x,y+1)]
                self.hcorners[(x,y)] = hs
                self.hcmax[(x,y)] = max(hs)
                self.h[(x,y)] = sum(hs)/4.0
                self.grad[(x,y)] = hs[2]-hs[0], hs[3]-hs[1]
            yield
        self.ready = True

    def getheight(self, x, y):
        if not self.ready:
            for _ in self.compute():
                pass
        if (x,y) in self.h: return self.h[(x, y)]
        X, Y = (x + y) / 2, (-x + y) / 2
        iX, iY = int(X), int(Y)
        ix, iy = iX - iY, iX + iY
        tX, tY = X - iX, Y - iY
        return ((self.h[(ix,iy)] * (1-tX) + self.h[(ix+1,iy+1)] * tX) * (1-tY) + 
                (self.h[(ix-1,iy-1)] * (1-tX) + self.h[(ix,iy+2)] * tX) * tY)        

    # x and y must be integers
    def getiheight(self, x, y):
        if not self.ready:
            for _ in self.compute():
                pass
        return self.h[(x, y)]

    def getigrad(self, x, y):
        if not self.ready:
            for _ in self.compute():
                pass
        return self.grad[(x, y)]


class parceldict(defaultdict):
    def __missing__(self, key):
        x, y = key
        ret = self[key] = Parcel(x*parcelsize, y*parcelsize)
        return ret
parcels = parceldict()
def height(x, y):
    return parcels[(int(x//parcelsize), int(y//parcelsize))].getheight(x, y)
def iheight(x, y):
    return parcels[(int(x//parcelsize), int(y//parcelsize))].getiheight(int(x//1), int(y//1))
def igrad(x, y):
    return parcels[(int(x//parcelsize), int(y//parcelsize))].getigrad(int(x//1), int(y//1))


def tileinfo(x, y):
    x, y = int(x//1), int(y//1)
    h = iheight(x, y)
    gx, gy = igrad(x, y)
    ps = []
    ps.append(camera.screenpos(x-1, y, iheight(x-1, y)))
    ps.append(camera.screenpos(x, y-1, iheight(x, y-1)))
    ps.append(camera.screenpos(x+1, y, iheight(x+1, y)))
    ps.append(camera.screenpos(x, y+1, iheight(x, y+1)))
    return h, gx, gy, ps

def minimap(x0, y0, w, h):
    s = pygame.Surface((w, h)).convert()
    for y in range(h):
        for x in range(w):
            s.set_at((x, y), hcolor(iheight(x0-w//2+x, y0+h//2-y), 0, 0))
    return s

# test scene
class WorldViewScene(object):
    def __init__(self):
        self.next = self

    def process_input(self, events, pressed):
        camera.x0 += 1.0 * (pressed['right'] - pressed['left'])
        camera.y0 += 1.0 * (pressed['up'] - pressed['down'])

    def update(self):
        pass

    def render(self, screen):
        screen.fill((0,0,0))
        x0, x1 = camera.xbounds()
        x0, x1 = int(x0 // 1) - 1, int(x1 // 1) + 2
        y0 = int(camera.y0)
        onscreen, y = True, y0
        while onscreen:
            onscreen = False
            for x in range(x0, x1):
                if (x + y) % 2: continue
                h, gx, gy, ps = tileinfo(x, y)
                pygame.draw.polygon(screen, hcolor(h, gx, gy), ps)
#                pygame.draw.lines(screen, (100,100,100), True, ps, 1)
                if max(py for px, py in ps) > 0:
                    onscreen = True
            y += 1
        onscreen, y = True, y0 - 1
        while onscreen:
            onscreen = False
            for x in range(x0, x1):
                if (x + y) % 2: continue
                h, gx, gy, ps = tileinfo(x, y)
                pygame.draw.polygon(screen, hcolor(h, gx, gy), ps)
#                pygame.draw.lines(screen, (100,100,100), True, ps, 1)
                if min(py for px, py in ps) < 600:
                    onscreen = True
            y -= 1
        pygame.draw.rect(screen, (255, 255, 255), (10, 10, 40, 40))
        screen.blit(minimap(int(camera.x0), int(camera.y0), 36, 36), (12, 12))


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


