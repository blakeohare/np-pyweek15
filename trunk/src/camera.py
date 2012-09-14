# Singleton module that controls camera view

try:
	from src import settings
except:
	from serverlib import settings

# Offset of the center of the screen, in pixels
x0 = 0
y0 = 0

# Give screen coordinates given world coordinates
def screenpos(x, y, z = 0):
    return int((x * settings.tilex)//1 - x0//1 + settings.sx//2), int(-(y * settings.tiley)//1 - y0//1 - (z * settings.tilez)//1 + settings.sy//2)

# Move the camera in the direction of the given world coordinates
def track(x, y, z = 0, f = None):
    if f is None: f = settings.trackvalue
    global x0, y0
    dx, dy = screenpos(x, y, z)
    dx -= settings.sx // 2
    dy -= settings.sy // 2
    x0 += dx * f
    y0 += dy * f

# Immediately point the camera at the given world coordinates
def lookat(x, y, z = 0):
    track(x, y, z, 1)

# whether the point is within margin pixels of the screen
def isvisible(px, py, margin=100):
    return -margin <= px <= settings.sx + margin and -margin <= py <= settings.sy + margin

# This is in pixel coordinates. A completely diff coordinate system.
def rectvisible(x, y, x1, y1):
	return x < x0 + settings.sx and x1 > x0 and y < y0 + settings.sy and y1 > y0


# A camera centered at the origin
class camera0:
    @staticmethod
    def screenpos(x, y, z = 0):
        return int((x * settings.tilex)//1 + settings.sx//2), int(-(y * settings.tiley)//1 - (z * settings.tilez)//1 + settings.sy//2)

