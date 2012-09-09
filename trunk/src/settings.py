# Module-level globals to keep constants in one handy place
# Attention players: don't mess with these settings!

import pygame


fps = 30   # maximum actual framerate

full_screen_mode = False
# resolution in windowed mode
# resolution here is the resolution of the virtual window - will be scaled up for display
wsx, wsy, wsz = 400, 300, 2
# minimum horizontal resolution in fullscreen mode
fsmin = 400


# pick the best resolution for fullscreen mode
def getfs():
	pygame.display.init()
	modes = pygame.display.list_modes()
	if not modes: return wsx, wsy, wsz
	mode0 = max(modes)
	# filter out modes that are the same resolution as the screen or too small
	modes = [(x,y) for x,y in modes if x*mode0[1] == y*mode0[0] and x > fsmin]
	x, y = min(modes)
	z = max(n for n in (1,2,3,4,5,6,7,8) if x % n == 0 and y % n == 0 and fsmin * n <= x)
	return int(x//z), int(y//z), z
fsx, fsy, fsz = getfs()

# size of the (un-zoomed) screen
sx, sy = wsx, wsy

# zoom factor
sz = wsz


trackvalue = 0.2

showminimap = False

# screen size for one unit in world coordinates
tilex, tiley, tilez = 16, 8, 2   

# Changing these will change the world map, so be careful!
noiseseed = 2117066982  # hash("one way trip")
rngcheck = 0.9908284413950574   # random.seed(noiseseed) ; random.random()
nmapsize = 64
tf0 = 0.03
tfactors = 1.000, 1.618, 2.618, 4.236, 6.854, 11.090, 17.944, 29.034
sealevel = -0.3
tscale = 30

# Size of a cached parcel
parcelsize = 40

# Size of a panel surface
panelw, panelh = 400, 300

# Size of a cached minimap chunk
mchunksize = 20

# tile border color with alpha (set to None to disable)
tbcolor = 128, 128, 128, 20
#tbcolor = None




