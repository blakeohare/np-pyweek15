import random, pygame, time, math
from collections import defaultdict
from src import camera, settings, images


# Python 2.5 shim
try:
    next
except NameError:
    def next(i):
        i.next()

# seed the RNG for reproducible noise map
try:
    random.seed(settings.noiseseed, version = 1)
except TypeError:
    random.seed(settings.noiseseed)
assert random.random() == settings.rngcheck, "Something wrong with the random number generation. Aborting!"
# Generate the noise map to be used for all terrain
noisemap = [[(random.random() * 2 - 1) * settings.tscale for x in range(settings.nmapsize)]
               for y in range(settings.nmapsize)]
noisemap = [row + row[0:1] for row in noisemap]
noisemap += noisemap[0:1]

# Reference implementation - slow
def noisevalue(x, y):
    x %= settings.nmapsize
    y %= settings.nmapsize
    tx, ty = x - int(x), y - int(y)
    x, y = int(x), int(y)
    return ((noisemap[x][y] * (1-tx) + noisemap[x+1][y] * tx) * (1-ty) + 
            (noisemap[x][y+1] * (1-tx) + noisemap[x+1][y+1] * tx) * ty)

# Reference implementation - slow
def height0(x, y):
    h = -settings.sealevel
    for f in settings.tfactors:
        h += noisevalue(x*f*settings.tf0, y*f*settings.tf0) / f
    if h > 0: h -= min(h/2, 20)
    return int(h)

def hcolor(h, gx, gy):
    a = 0.8 + 0.08 * gx
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
    xs = [xx*f*settings.tf0 % settings.nmapsize for f in settings.tfactors]
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

pcs = settings.parcelsize
class Parcel(object):
    def __init__(self, x0, y0):
        self.x0, self.y0 = x0, y0
        self.ready = False
        self.compiter = self.compute()

    def compute(self):
        dpextend(min(self.x0, self.y0) - 4, max(self.x0, self.y0) + pcs + 4)
        yield
        # Determine heights for corners
        self.h = {}
        for y in range(self.y0 - 3, self.y0 + pcs + 4):
            for x in range(self.x0 - 3 + y % 2, self.x0 + pcs + 5, 2):
                # TODO: easy integer map to actual h values
                h = -settings.sealevel
                for f, (xx, tx), (yy, ty) in zip(settings.tfactors, dpcache[x], dpcache[y]):
                    h += ((noisemap[xx][yy] * (1-tx) + noisemap[xx+1][yy] * tx) * (1-ty) + 
                        (noisemap[xx][yy+1] * (1-tx) + noisemap[xx+1][yy+1] * tx) * ty) / f
                if h > 0: h -= min(h/2, 20)
                self.h[(x, y)] = max(int(h), 0)
            yield
        self.hcorners = {}
        self.hcmax = {}
        self.grad = {}
        # Determine heights for tiles
        for y in range(self.y0 - 2, self.y0 + pcs + 3):
            for x in range(self.x0 - 2 + y % 2, self.x0 + pcs + 4, 2):
                hs = self.h[(x-1,y)], self.h[(x,y-1)], self.h[(x+1,y)], self.h[(x,y+1)]
                self.hcorners[(x,y)] = hs
                self.hcmax[(x,y)] = max(hs)
                self.h[(x,y)] = sum(hs)/4.0
                self.grad[(x,y)] = hs[2]-hs[0], hs[3]-hs[1]
            yield
        self.ready = True

    def getheight(self, x, y):
        if self.compiter:
            for _ in self.compiter:
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
        if self.compiter:
            for _ in self.compiter:
                pass
        return self.h[(x, y)]

    def getigrad(self, x, y):
        if self.compiter:
            for _ in self.compiter:
                pass
        return self.grad[(x, y)]

    def getihcmax(self, x, y):
        if self.compiter:
            for _ in self.compiter:
                pass
        return self.hcmax[(x, y)]

    def getihcorners(self, x, y):
        if self.compiter:
            for _ in self.compiter:
                pass
        return self.hcorners[(x, y)]


class parceldict(defaultdict):
    def __missing__(self, key):
        x, y = key
        ret = self[key] = Parcel(x*pcs, y*pcs)
        return ret
parcels = parceldict()
parcelq = []

def height(x, y):
    return parcels[(int(x//pcs), int(y//pcs))].getheight(x, y)
def iheight(x, y):
    return parcels[(int(x//pcs), int(y//pcs))].getiheight(int(x//1), int(y//1))
# maximum height of any of this tile's 4 corners
def ihcmax(x, y):
    return parcels[(int(x//pcs), int(y//pcs))].getihcmax(int(x//1), int(y//1))
# heights of the four corners
def ihcorners(x, y):
    return parcels[(int(x//pcs), int(y//pcs))].getihcorners(int(x//1), int(y//1))
def igrad(x, y):
    return parcels[(int(x//pcs), int(y//pcs))].getigrad(int(x//1), int(y//1))
def addparcels(x, y):
    x0, y0 = int(x // pcs), int(y // pcs)
    for x in range(x0-3, x0+4):
        for y in range(y0-3, y0+4):
            if (x,y) not in parcels:
                p = Parcel(x*pcs,y*pcs)
                parcels[(x,y)] = p
                parcelq.append(p)
def thinkparcels(dt=0):
    if not parcelq:
        return 0
    tf = time.time() + dt if dt else 0
    n = 0
    while True:
        n += 1
        if parcelq[0].compiter:
            try:
                next(parcelq[0].compiter)
            except StopIteration:
                parcelq.pop(0)
        else:
            parcelq.pop(0)
        if time.time() > tf or not parcelq:
            return n




def tileinfo(x, y, looker=None):
    looker = looker or camera
    x, y = int(x//1), int(y//1)
    h = iheight(x, y)
    gx, gy = igrad(x, y)
    ps = []
    ps.append(looker.screenpos(x-1, y, iheight(x-1, y)))
    ps.append(looker.screenpos(x, y-1, iheight(x, y-1)))
    ps.append(looker.screenpos(x+1, y, iheight(x+1, y)))
    ps.append(looker.screenpos(x, y+1, iheight(x, y+1)))
    return h, gx, gy, ps

def minimap(x0, y0, w, h):
    # TODO: cache me
    s = pygame.Surface((w, h)).convert()
    for y in range(h):
        for x in range(w):
            s.set_at((x, y), hcolor(iheight(x0-w//2+x, y0+h//2-y), 0, 0))
    return s


# A cached version of the landscape, for fast blitting
class Panel(object):
    def __init__(self, x0, y0):
        self.x0 = x0
        self.y0 = y0
        self.w, self.h = settings.panelw, settings.panelh
        self.ready = False
        self.compiter = self.compute()

    def screenpos(self, x, y, z):
        return int(x * settings.tilex - self.x0 * self.w), int(-self.y0 * self.h - y * settings.tiley - z * settings.tilez)

    def compute(self):
        self.surf = pygame.Surface((self.w, self.h)).convert()
        self.lines = bool(settings.tbcolor)
        if self.lines:
            lsurf = pygame.Surface((self.w, self.h)).convert_alpha()
            lsurf.fill((0,0,0,0))
        x0 = int(self.x0 * self.w / settings.tilex // 1) - 1
        x1 = int((self.x0 + 1) * self.w / settings.tilex // 1) + 2
        y0 = int(-(self.y0 + 1) * self.h / settings.tiley // 1)
        onscreen, y = True, y0
        while onscreen:
            onscreen = False
            for x in range(x0, x1):
                if (x + y) % 2: continue
                h, gx, gy, ps = tileinfo(x, y, self)
                pygame.draw.polygon(self.surf, hcolor(h, gx, gy), ps)
                if self.lines:
                    pygame.draw.lines(lsurf, settings.tbcolor, False, ps[0:3], 1)
                if max(py for px, py in ps) > 0:
                    onscreen = True
                yield
            y += 1
        onscreen, y = True, y0 - 1
        while onscreen:
            onscreen = False
            for x in range(x0, x1):
                if (x + y) % 2: continue
                h, gx, gy, ps = tileinfo(x, y, self)
                pygame.draw.polygon(self.surf, hcolor(h, gx, gy), ps)
                if self.lines:
                    pygame.draw.lines(lsurf, settings.tbcolor, False, ps[0:3], 1)
                if min(py for px, py in ps) < self.h:
                    onscreen = True
                yield
            y -= 1
        if self.lines:
            self.surf.blit(lsurf, (0,0))
        self.ready = True

    def getsurf(self):
        if self.compiter:
            for _ in self.compiter:
                pass
        return self.surf

panels = {}
panelq = []
def drawpanels(surf, x0, y0, w, h):
    for x in range(int(x0 // settings.panelw), int((x0 + w) // settings.panelw) + 1):
        for y in range(int(y0 // settings.panelh), int((y0 + h) // settings.panelh) + 1):
            if (x,y) not in panels:
                panels[(x,y)] = Panel(x, y)
            s = panels[(x, y)].getsurf()
            surf.blit(s, (x * settings.panelw - x0, y * settings.panelh - y0))
def addpanels(x, y):
    x0, y0 = int(x // settings.panelw), int(y // settings.panelh)
    for x in range(x0-2, x0+3):
        for y in range(y0-2, y0+3):
            if (x,y) not in panels:
                p = Panel(x,y)
                panels[(x,y)] = p
                panelq.append(p)
def thinkpanels(dt=0):
    if not panelq:
        return 0
    tf = time.time() + dt if dt else 0
    n = 0
    while True:
        n += 1
        if panelq[0].compiter:
            try:
                next(panelq[0].compiter)
            except StopIteration:
                panelq.pop(0)
        else:
            panelq.pop(0)
        if time.time() > tf or not panelq:
            return n


# test building drawing - will definitely change
def drawbuildingat(screen, btype, x, y, z):
    px, py = camera.screenpos(x, y, z)
    if not camera.isvisible(px, py, 100):
        return
    drawplatformat(screen, x, y)
    img = images.get_image("buildings/%s.png" % btype)
    ix, iy = img.get_size()
    screen.blit(img, (px-ix//2, py-iy+ix//4))

def drawplatformat(screen, x, y):
    z0, z1, z2, z3 = ihcorners(x, y)
    zm = max((z0, z1, z2, z3))
    p0,p1,p2,p3,p4,p5,p6 = [camera.screenpos(a,b,c) for a,b,c in
            ((x-1,y,zm), (x,y-1,zm), (x+1,y,zm), (x,y+1,zm), (x-1,y,z0), (x,y-1,z1), (x+1,y,z2))]
    # left
    pygame.draw.polygon(screen, (0,100,100), (p0,p4,p5,p1))
    # right
    pygame.draw.polygon(screen, (0,50,50), (p1,p5,p6,p2))
    # top
    pygame.draw.polygon(screen, (0,70,70), (p0,p1,p2,p3))


# test scene
class WorldViewScene(object):
    def __init__(self):
        self.next = self
        self.guyx, self.guyy = 1234, 3456
        camera.lookat(self.guyx, self.guyy)
        
        self.buildings = []
        for j in range(100):
            y = int(self.guyy // 1) + random.randint(-50, 50)
            x = int(self.guyx // 1) + random.randint(-50, 50)
            if (x + y) % 2: continue
            z = ihcmax(x, y)
            if z <= 0: continue
            btype = random.choice(["hq", "greenhouse"])
            self.buildings.append((btype, x, y, z))

    def process_input(self, events, pressed):
        self.guyx += 0.25 * (pressed['right'] - pressed['left'])
        self.guyy += 0.25 * (pressed['up'] - pressed['down'])

    def update(self):
        self.guyz = height(self.guyx, self.guyy)
        camera.track(self.guyx, self.guyy, self.guyz)
        addpanels(camera.x0, camera.y0)
        addparcels(camera.x0 / settings.tilex, -camera.y0 / settings.tiley)
#        print len(panels), len(panelq), thinkpanels(0.005), len(parcels), len(parcelq), thinkparcels(0.005)
        thinkparcels(0.005)
        thinkpanels(0.005)

    def render(self, screen):
        screen.fill((0,0,0))
        drawpanels(screen, camera.x0//1-settings.sx//2, camera.y0//1-settings.sy // 2, settings.sx, settings.sy)
        # background buildings
        for btype, x, y, z in self.buildings:
            if y > self.guyy:
                drawbuildingat(screen, btype, x, y, z)
        # bouncy ball
        px, py = camera.screenpos(self.guyx, self.guyy, self.guyz)
        pygame.draw.ellipse(screen, (0, 0, 0), (px-4, py-2, 8, 4))
        h = int(abs(10 * math.sin(7 * time.time())))
        pygame.draw.circle(screen, (255, 0, 0), (px, py-4-h), 4)
        # foreground buildings
        for btype, x, y, z in self.buildings:
            if y <= self.guyy:
                drawbuildingat(screen, btype, x, y, z)


#        pygame.draw.rect(screen, (255, 255, 255), (10, 10, 40, 40))
#        screen.blit(minimap(int(camera.x0 // settings.tilex), -int(camera.y0 // settings.tiley), 36, 36), (12, 12))


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


