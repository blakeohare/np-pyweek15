# Rendering of the world map

import random, pygame, time, math
from collections import defaultdict
from src import camera, settings, images, terrain, gtexture

# Python 2.5 shim
try:
    next
except NameError:
    def next(i):
        return i.next()

def highlighttile(surf, x, y, looker=None):
    x, y = terrain.nearesttile(x, y)
    h, h0, (gx, gy), ps = terrain.tileinfo(x, y, looker)
    x0, x1 = min(x for x,y in ps), max(x for x,y in ps)
    y0, y1 = min(y for x,y in ps), max(y for x,y in ps)
    s = pygame.Surface(((x1-x0+1), (y1-y0+1))).convert_alpha()
    s.fill((0,0,0,0))
    ps = [(x-x0,y-y0) for x,y in ps]
    pygame.draw.polygon(s, (255, 0, 0, 50), ps)
#    pygame.draw.lines(s, (255, 0, 0, 100), True, ps, 1)
    surf.blit(s, (x0,y0))

def drawfadinggrid(surf, xc, yc, r=None, looker=None):
    r = settings.cursorgridsize if r is None else r
    looker = looker or camera
    x0, y0 = terrain.nearesttile(xc, yc)
    s = pygame.Surface(surf.get_size()).convert_alpha()
    s.fill((0,0,0,0))
    hs, ps, alphas = {}, {}, {}
    for dx in range(-r, r+2):
        for dy in range(-r, r+2):
            x, y = x0 - 1 + dx + dy, y0 + dx - dy
            h = terrain.iheight(x, y)
            hs[(dx,dy)] = h
            ps[(dx,dy)] = looker.screenpos(x, y, h)
            alphas[(dx,dy)] = 1 - math.sqrt(((x-xc)**2 + (y-yc)**2) / (r+1)**2)
    for dx in range(-r, r+1):
        for dy in range(-r, r+2):
            if hs[(dx,dy)] or hs[(dx+1,dy)]:
                a = min(max(int(50 * (alphas[(dx,dy)] + alphas[(dx+1,dy)])), 0), 255)
                pygame.draw.line(s, (255,255,255,a), ps[(dx,dy)], ps[(dx+1,dy)])
            if hs[(dy,dx)] or hs[(dy,dx+1)]:
                a = min(max(int(50 * (alphas[(dy,dx)] + alphas[(dy,dx+1)])), 0), 255)
                pygame.draw.line(s, (255,255,255,a), ps[(dy,dx)], ps[(dy,dx+1)])
    surf.blit(s, (0, 0))

minimaps = {}
def minichunk(x0, y0):
    if (x0, y0) not in minimaps:
        t0 = time.time()
        a = settings.mchunksize
        s = pygame.Surface((a, a))
#        arr = pygame.surfarray.pixels3d(s)
        for y in range(a):
            for x in range(-1,a):
                if (x + y) % 2 == 0: continue
                h, h0, (gx, gy), ps = terrain.tileinfo(x0*a+x, y0*a+(a-1-y))
                g = gx * settings.lightx + gy * settings.lighty
                c = gtexture.hcolor(h, h0, g)
                s.set_at((x, y), c)
                s.set_at((x+1, y), c)
#                arr[x,y,:] = gtexture.hcolor(terrain.iheight(x0*a+x, y0*a+(a-1-y)), 0, 0)
        minimaps[(x0,y0)] = s.convert()
#        print(x0, y0, time.time() - t0)
    return minimaps[(x0,y0)]
# return a minimap centered at (x, y) with size (w, h)
def minimap(x, y, w, h):
    s = pygame.Surface((w, h)).convert()
    a = settings.mchunksize
    x0 = int((x-w//2)//a)
    x1 = int((x+w//2)//a)
    y0 = int((y-h//2)//a)
    y1 = int((y+h//2)//a)
    for ay in range(y0,y1+1):
        for ax in range(x0,x1+1):
            s.blit(minichunk(ax,ay), (ax*a - (x-w//2), (-ay-1)*a + y + h//2))
    return s
def dumpmap():
    if not minimaps: return
    x0 = min(x for x,y in minimaps)
    x1 = max(x for x,y in minimaps) + 1
    y0 = min(y for x,y in minimaps)
    y1 = max(y for x,y in minimaps) + 1
    a = settings.mchunksize
    s = pygame.Surface((a*(x1-x0), a*(y1-y0)))
    s.fill((0,0,0))
    for x in range(x0, x1):
        for y in range(y0, y1):
            if (x,y) not in minimaps: continue
            s.blit(minimaps[(x,y)], (a*(x-x0), a*(y1-1-y)))
    pygame.image.save(s, "map.png")
def thinkminimap(dt=0):
    tf = time.time() + dt if dt else 0
    tf = 0
    n = 0
    x0 = int(camera.x0 / settings.tilex // settings.mchunksize)
    y0 = int(-camera.y0 / settings.tiley // settings.mchunksize)
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            if (x0+dx, y0+dy) not in minimaps:
                minichunk(x0+dx, y0+dy)
                n += 1
            if time.time() > tf:
                return n

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
                h, h0, (gx, gy), ps = terrain.tileinfo(x, y, self)
                g = gx * settings.lightx + gy * settings.lighty
                gtexture.putterrain(self.surf, h, h0, g, ps)
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
                h, h0, (gx, gy), ps = terrain.tileinfo(x, y, self)
                g = gx * settings.lightx + gy * settings.lighty
                gtexture.putterrain(self.surf, h, h0, g, ps)
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
    x0, y0 = int(camera.x0 // settings.panelw), int(camera.y0 // settings.panelh)
    if not panelq:
        return 0
    tf = time.time() + dt if dt else 0
    n = 0
    while True:
        n += 1
        topop = False
        if panelq[0].compiter:
            try:
                next(panelq[0].compiter)
            except StopIteration:
                topop = True
        else:
            topop = True
        if topop:
            panelq.pop(0)
            panelq.sort(key = lambda p: (x0 - p.x0) ** 2 + (y0 - p.y0) ** 2)
        if time.time() > tf or not panelq:
            return n

# Call this function when you've got a little time to kill and you might as well
# be doing something useful.
def killtime(dt=0):
    terrain.addparcels(camera.x0 / settings.tilex, -camera.y0 / settings.tiley)
    addpanels(camera.x0, camera.y0)
    tf = time.time() + dt
    n = 0
    while time.time() < tf:
        dt = tf - time.time()
        m = terrain.thinkparcels(0.5 * dt)
        m += thinkpanels(0.4 * dt) 
        m += thinkminimap(0.1 * dt)
        if not m: break
        n += m
    return n
def killtimequeuesize():
    return len(terrain.parcelq), len(panelq)


def drawscene(screen, entities, cursorpos = None):
    screen.fill((0,0,0))
    drawpanels(screen, camera.x0//1-settings.sx//2, camera.y0//1-settings.sy // 2, settings.sx, settings.sy)
    if cursorpos:
        cx, cy = cursorpos
        highlighttile(screen, cx, cy)
        drawfadinggrid(screen, cx, cy)
    esort = sorted(entities, key = lambda e: -e.y)
    for entity in esort:
        entity.render(screen)

def drawminimap(screen):
    a = settings.minimapsize
    pygame.draw.rect(screen, (255, 255, 255), (10, 10, a + 2, a + 2))
    screen.blit(minimap(int(camera.x0 // settings.tilex), -int(camera.y0 // settings.tiley), a, a), (11, 11))


if __name__ == "__main__":
    import pygame
    from pygame import *
    screen = display.set_mode((800, 600))
    display.set_caption("Don't worry, the real game will be much faster at this.")
    for y in range(600):
        for x in range(800):
            h = terrain.height(x, y)
            c = hcolor(h)
            screen.set_at((x, y), c)
        draw.rect(screen, (255, 255, 255), (100, 100, 20, 30), 1)
        pygame.display.flip()
        if any(event.type in (KEYDOWN, QUIT) for event in pygame.event.get()):
            exit()
    while not any(event.type in (KEYDOWN, QUIT) for event in pygame.event.get()):
        pass
    image.save(screen, "map-example.png")


