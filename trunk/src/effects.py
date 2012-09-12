# A list of special effects that don't affect the gameplay.
# It's really easier to just give in and make this a singleton, rather than passing around a list
#   everywhere that any entity can append to.

# Effects should have an alive attribute, an update method, and a render method
# They need to at least have a y-coordinate, for drawing order.
# Effects are not rendered on the minimap

import pygame
from src import camera

effects = []

def update():
    global effects
    for e in effects:
        e.update()
    effects = [e for e in effects if e.alive]

def add(e):
    effects.append(e)

class LaserBeam(object):
    color = 128,128,255
    lifetime = 4
    def __init__(self, x0, y0, z0, x1, y1, z1):
        self.x0, self.y0, self.z0 = x0, y0, z0
        self.x1, self.y1, self.z1 = x1, y1, z1
        self.y = (self.y0 + self.y1) / 2.
        self.t = 0
        self.alive = True
    def update(self):
        self.t += 1
        self.alive = self.t <= self.lifetime
    def render(self, screen, looker=None):
        looker = looker or camera
        p0 = looker.screenpos(self.x0, self.y0, self.z0)
        p1 = looker.screenpos(self.x1, self.y1, self.z1)
        pygame.draw.line(screen, self.color, p0, p1, 2)



