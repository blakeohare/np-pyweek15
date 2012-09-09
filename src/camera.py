# Singleton module that controls camera view


tilex, tiley, tilez = 16, 8, 2   # pixel sizes for one tile


x0 = 0
y0 = 0
sx = 400
sy = 300

# Give screen coordinates given world coordinates
def screenpos(x, y, z = 0):
    return int((x - x0) * tilex + sx/2), int(-(y - y0) * tiley - z * tilez + sy/2)

# westernmost and easternmost longitude that appears on the screen
def xbounds():
    return x0 - sx / 2.0 / tilex, x0 + sx / 2.0 / tilex


