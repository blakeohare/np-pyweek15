import pygame, math
from src import worldmap, camera, settings

class Sprite(object):
    def __init__(self, x, y, z=None):
        self.x, self.y = x, y
        self.z = worldmap.height(self.x, self.y) if z is None else z

    def lookatme(self):
        camera.lookat(self.x, self.y, worldmap.height(self.x, self.y))

    def trackme(self):
        camera.track(self.x, self.y, worldmap.height(self.x, self.y), settings.trackvalue)

    def rendershadow(self, screen):
        px, py = camera.screenpos(self.x, self.y, worldmap.height(self.x, self.y))
        pygame.draw.ellipse(screen, (0, 0, 0), (px-4, py-2, 8, 4))

    def update(self):
        pass

# Just a bouncing ball for now
class You(Sprite):
    v = 0.4  # tiles per frame
    
    def move(self, dx, dy):
        self.x += dx * self.v
        self.y += dy * self.v

    def update(self):
        import time
        self.z = worldmap.height(self.x, self.y) + int(abs(5 * math.sin(7 * time.time())))

    def render(self, screen):
        self.rendershadow(screen)
        px, py = camera.screenpos(self.x, self.y, self.z)
        pygame.draw.circle(screen, (255, 0, 0), (px, py-4), 4)

