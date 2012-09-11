# Just messing around trying to get a good height profile

import random

class settings:
    noiseseed = 2117066982  # hash("one way trip")
    rngcheck = 0.9908284413950574   # random.seed(noiseseed) ; random.random()
    tf0 = 0.03
    tfactors = 1.000, 1.618, 2.618, 4.236, 6.854, 11.090, 17.944, 29.034
    # ", ".join(["%.2f" % (random.random() * 256) for _ in range(8)])
    toffsets = 140.08, 192.23, 234.93, 139.46, 105.50, 81.69, 152.01, 226.66
    sealevel = -0.33
    tscale = 16
    nmapsize = 64


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
    for f, o in zip(settings.tfactors, settings.toffsets):
        h += noisevalue(x*f*settings.tf0 + o, y*f*settings.tf0 + o) / f
    h *= settings.tscale
    h += 0.6*(max(h-16,0) + max(h-20,0))
#    return h
#    if h > 0: h -= min(h/2, 20)
    return int(h//1)

random.seed()
for j in range(1):
    hs = [height0(random.uniform(-2000,2000), random.uniform(-2000,2000)) for _ in range(100000)]
#    print min(hs), max(hs), sum(h > 16 for h in hs)/100000., sum(h > 20 for h in hs)/100000., sum(h > 24 for h in hs)/100000.
    for h in hs:
        print h


