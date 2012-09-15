# Module-level globals to keep constants in one handy place
# Attention players: don't mess with these settings!

import sys

fps = 30   # maximum actual framerate

full_screen_mode = False
# resolution in windowed mode
# resolution here is the resolution of the virtual window - will be scaled up for display
wsx, wsy, wsz = 400, 300, 2
if "--small" in sys.argv:
	wsz = 1
if "--large" in sys.argv:
	wsz = 3

# minimum horizontal resolution in fullscreen mode
fsmin = 400

show_verbose_output = True

# pick the best resolution for fullscreen mode
def getfs():
	import pygame
	pygame.display.init()
	modes = pygame.display.list_modes()
	if not modes: return wsx, wsy, wsz
	mode0 = max(modes)
	# filter out modes that are the same resolution as the screen or too small
	modes = [(x,y) for x,y in modes if x*mode0[1] == y*mode0[0] and x > fsmin]
	x, y = min(modes)
	z = max(n for n in (1,2,3,4,5,6,7,8) if x % n == 0 and y % n == 0 and fsmin * n <= x)
	return int(x//z), int(y//z), z
#try:
#	fsx, fsy, fsz = getfs()
#except ImportError:
#	fsx, fsy, fsz = wsx, wsy, wsz
fsx, fsy, fsz = wsx, wsy, wsz


# size of the (un-zoomed) screen
sx, sy = wsx, wsy

# zoom factor
sz = wsz


playmusic = "--nomusic" not in sys.argv
playsfx = "--nosfx" not in sys.argv


attackblake = "--attackblake" in sys.argv

cursorgridsize = 4

trackvalue = 0.2

showminimap = True
minimapsize = 64
minimappos = -72, -72
dumpmap = False

# screen size for one unit in world coordinates
tilex, tiley, tilez = 16, 8, 2   

# Changing these will change the world map, so be careful!
noiseseed = 2117066982  # hash("one way trip")
rngcheck = 0.9908284413950574   # random.seed(noiseseed) ; random.random()
nmapsize = 64
tf0 = 0.03
tfactors = 1.000, 1.618, 2.618, 4.236, 6.854, 11.090, 17.944, 29.034
# ", ".join(["%.2f" % (random.random() * 256) for _ in range(8)])
toffsets = 140.08, 192.23, 234.93, 139.46, 105.50, 81.69, 152.01, 226.66
sealevel = -0.33
tscale = 16
tstepsize = 0.3
tsteps = 16, 20

# Size of a cached parcel
parcelsize = 40

# Size of a panel surface
panelw, panelh = 400, 300

lightx, lighty = 0.1, 0.1

# Size of a cached minimap chunk
mchunksize = 20

# tile border color with alpha (set to None to disable)
tbcolor = 128, 128, 128, 20
tbcolor = None

usetgradient = True



RESOURCE_FOOD = "Num nums"
RESOURCE_WATER = "Wawa"
RESOURCE_ALUMINUM = "Shinyium"
RESOURCE_COPPER = "Rust"
RESOURCE_SILICON = "Obtainium"
RESOURCE_OIL = "Dark Chocolate"


building_cost = {
# food, water, aluminum, copper, silicon, oil

'hq':           [50, 50, 100, 0, 0, 0],
'drill':        [50, 50, 100, 0, 0, 0],
'foundry':      [50, 50, 100, 0, 0, 0],
'beacon':       [50, 50, 100, 0, 0, 0],
'machinerylab': [50, 50, 100, 0, 0, 0],
'sciencelab':   [50, 50, 100, 0, 0, 0],
'launchsite':   [50, 50, 100, 0, 0, 0],
'farm':         [50, 50, 100, 0, 0, 0],
'greenhouse':   [50, 50, 100, 0, 0, 0],
'medicaltent':  [50, 50, 100, 0, 0, 0],
'quarry':       [50, 50, 100, 0, 0, 0],
'radar':        [50, 50, 100, 0, 0, 0],
'turret':       [50, 50, 100, 0, 0, 0],
'fireturret':   [50, 50, 100, 0, 0, 0],
'lazorturret':  [50, 50, 100, 0, 0, 0],
'teslaturret':  [50, 50, 100, 0, 0, 0],
'resevoir':     [50, 50, 100, 0, 0, 0]
}

building_size = {
	'hq': 1,
	'drill': 1,
	'foundry': 1,
	'beacon': 1,
	'machinerylab': 1,
	'sciencelab': 1,
	'launchsite': 2,
	'farm': 2,
	'greenhouse': 1,
	'medicaltent': 1,
	'quarry': 2,
	'radar': 1,
	'turret': 1,
	'fireturret': 1,
	'lazorturret': 1,
	'teslaturret': 1,
	'resevoir': 2
}

building_research = {
	'hq': 0,
	'greenhouse': 0,
	'medicaltent': 0,
	'turret': 0,
	'farm': 50,
	'quarry': 75,
	'resevoir': 100,
	'beacon': 150,
	'drill': 200,
	'fireturret': 225,
	'radar': 250,
	'foundry': 275,
	'machinerylab': 300,
	'teslaturret': 325,
	'lazorturret': 350,
	'sciencelab': 400,
	'launchsite': 600
}


botnames = "CheapBot", "QuickBot", "StrongBot"


BOT_COST_1 = {
	'food': 0,
	'water': 0,
	'aluminum': 50,
	'copper': 25,
	'silicon': 10,
	'oil': 0
}

BOT_COST_2 = {
	'food': 0,
	'water': 0,
	'aluminum': 200,
	'copper': 100,
	'silicon': 50,
	'oil': 50
}

BOT_COST_3 = {
	'food': 0,
	'water': 0,
	'aluminum': 500,
	'copper': 300,
	'silicon': 700,
	'oil': 150
}

ALIEN_DROPS = [
	{ 'food': 25, 'aluminum': 10, 'copper': 5, 'silicon': 15 },
	{ 'food': 50, 'water': 100, 'aluminum': 0, 'copper': 10, 'silicon': 50 },
	{ 'oil': 150, 'silicon': 100 }
]