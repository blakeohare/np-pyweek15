# Singleton module that controls camera view


tilex, tiley, tilez = 16, 8, 2   # pixel sizes for one tile


x0 = 0
y0 = 0
sx = 400
sy = 300

# Give screen coordinates given world coordinates
def screenpos(x, y, z = 0):
    return int(x * tilex - x0 + sx/2), int(-y * tiley - y0 - z * tilez + sy/2)



