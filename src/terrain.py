# The math behind terrain generation

import random, time
from collections import defaultdict
from src import settings, camera

# Convert between axis-aligned (render) coordinates and tilted (model) coordinates
def toModel(x, y):
    return (x-y)/2, (-x-y)/2
def toRender(X, Y):
    return X-Y, -X-Y

# Python 2.5 shim
try:
    next
except NameError:
    def next(i):
        return i.next()

# seed the RNG for reproducible noise map
try:
    random.seed(settings.noiseseed, version = 1)
except TypeError:
    random.seed(settings.noiseseed)
assert random.random() == settings.rngcheck, "Something wrong with the random number generation. Aborting!"
# Generate the noise map to be used for all terrain
noisemap = [[(random.random() * 2 - 1) for x in range(settings.nmapsize)]
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
    h *= settings.tscale
    if h > 0: h -= min(h/2, 20)
    return int(h)

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
        for y in range(self.y0 - 3, self.y0 + pcs + 5):
            for x in range(self.x0 - 3 + y % 2, self.x0 + pcs + 5, 2):
                # TODO: easy integer map to actual h values
                h = -settings.sealevel
                for f, (xx, tx), (yy, ty) in zip(settings.tfactors, dpcache[x], dpcache[y]):
                    h += ((noisemap[xx][yy] * (1-tx) + noisemap[xx+1][yy] * tx) * (1-ty) + 
                        (noisemap[xx][yy+1] * (1-tx) + noisemap[xx+1][yy+1] * tx) * ty) / f
                h *= settings.tscale
                if h > 0: h -= min(h/2, 20)
                self.h[(x, y)] = max(int(h), 0)
            yield
        self.hcorners = {}
        self.hcmax = {}
        self.grad = {}
        # Determine heights for tiles
        for y in range(self.y0 - 2, self.y0 + pcs + 4):
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
        iX, iY = int(X//1), int(Y//1)
        ix, iy = iX - iY, iX + iY
        tX, tY = X - iX, Y - iY
        return ((self.h[(ix,iy)] * (1-tX) + self.h[(ix+1,iy+1)] * tX) * (1-tY) + 
                (self.h[(ix-1,iy-1)] * (1-tX) + self.h[(ix,iy+2)] * tX) * tY)

    def complete(self):
        if self.compiter:
            for _ in self.compiter:
                pass
            self.compiter = None

    # x and y must be integers
    def getiheight(self, x, y):
        self.complete()
        return self.h[(x, y)]

    def getigrad(self, x, y):
        self.complete()
        return self.grad[(x, y)]

    def getihcmax(self, x, y):
        self.complete()
        return self.hcmax[(x, y)]

    def getihcorners(self, x, y):
        self.complete()
        return self.hcorners[(x, y)]


class parceldict(defaultdict):
    def __missing__(self, key):
        x, y = key
        ret = self[key] = Parcel(x*pcs, y*pcs)
        return ret
parcels = parceldict()
parcelq = []

def dumpparcels():
    import cPickle
    ks = list(parcels)
    for k in ks:
        if parcels[k].compiter:
            del parcels[k]
    cPickle.dump(parcels, open("parcel-dump-test.pkl", "wb"))

def nearesttile(x, y):
    X, Y = (x + y) / 2, (-x + y) / 2
    iX, iY = int((X+0.5)//1), int((Y+0.5)//1)
    return iX - iY, iX + iY
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
    x0, y0 = int(camera.x0 / settings.tilex // pcs), int(-camera.y0 / settings.tiley // pcs)
    if not parcelq:
        return 0
    tf = time.time() + dt if dt else 0
    n = 0
    while True:
        n += 1
        topop = False
        if parcelq[0].compiter:
            try:
                next(parcelq[0].compiter)
            except StopIteration:
                topop = True
        else:
            topop = True
        if topop:
            parcelq.pop(0)
            parcelq.sort(key = lambda p: (x0 - p.x0)**2 + (y0-p.y0)**2)
        if time.time() > tf or not parcelq:
            return n

# How far do you have to go along this track before you hit water?
def dtrack(x0, y0, track, dmax = 100):
    n = 0
    x, y = x0, y0
    while True:
        for dx, dy in track:
            n += 1
            x += dx
            y += dy
            if iheight(x, y) <= 0 or n >= dmax:
                return n

def validstart(x, y):
    x, y = int(x//1), int(y//1)
    # send out feelers in a variety of directions until they hit water
    if iheight(x, y) < 0: return False
    waterhits = []
    for a,b,c,d in [(1,0,0,1), (0,1,-1,0), (-1,0,0,-1), (0,-1,1,0)]:
        dx, dy = (b,d), (a,c)
        waterhits.append(dtrack(x, y, [dx]))
        waterhits.append(dtrack(x, y, [dx,dy]))
        waterhits.append(dtrack(x, y, [dx,dx,dx,dy]))
    ws = sorted(waterhits)[3:-3]
    return ws[0] > 1 and ws[3] > 5 and ws[-3] > 40 and ws[-1] > 60

def choosevalidstart():
    random.seed()
    print("Choosing starting location....")
    while True:
        x = random.randint(-2000, 2000)
        y = random.randint(-2000, 2000)
        if validstart(x, y):
            break
    print("(%s,%s) looks like a good place to start...." % (x, y))
    return x, y

# Obviously doesn't take into account whether there's anything already built there
def canbuildhere(x, y):
    return (x + y) % 2 == 0 and iheight(x, y) > 0



