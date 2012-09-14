import pygame
from src import camera, images, terrain, util, effects, settings

class Structure(object):
	minicolor = 192, 192, 192
	size = 1
	hp0 = 1
	attackable = False
	healthbarheight = 24
	flashdamage = 0
	# TODO: handle buildings with bigger footprints than 1x1
	def __init__(self, user_id, x, y, z=None):
		self.user_id = user_id
		self.landing_hack = False
		self.selected = False
		self.last_render_y = None
		self.x, self.y = terrain.toCenterRender(x, y)
		if self.size == 2: self.y -= 1
		if z is None:
			self.setheight(0)
		else:
			self.z = z
		self.hp = self.hp0
	
	def getModelXY(self):
		return terrain.toModel(self.x, self.y + 1)

	# All squares this building covers in render coordinates
	def rsquares(self):
		return [(self.x+dX-dY, self.y+self.size-1-dX-dY) for dX in range(self.size) for dY in range(self.size)]

	# All squares this building covers in model coordinates  -- not sure if this works yet
#	def msquares(self):
#		X, Y = int((self.x - self.y) // 2), int((-self.x - self.y)//2)
#		return [(X+dX, Y+dY) for dX in range(self.size) for dY in range(self.size)]

	def renderplatform(self, screen, looker=None):
		looker = looker or camera
		# TODO: this should probably be cached into an image
		x, y, z = self.x, self.y, self.z
		# TODO: this better
		if self.size == 1:
			z0, z1, z2, z3 = terrain.ihcorners(x, y)
			p0,p1,p2,p3,p4,p5,p6 = [looker.screenpos(a,b,c) for a,b,c in
					((x-1,y,z), (x,y-1,z), (x+1,y,z), (x,y+1,z), (x-1,y,z0), (x,y-1,z1), (x+1,y,z2))]
			leftps = p0, p4, p5, p1
			rightps = p1, p5, p6, p2
			topps = p0, p1, p2, p3
		elif self.size == 2:
			z0, z1, z2, z3, z4 = [terrain.iheight(x+dx,y+dy) for dx,dy in
				[(-2,0),(-1,-1),(0,-2),(1,-1),(2,0)]]
			b0,b1,b2,b3,b4,t0,t1,t2,t3 = [looker.screenpos(x+a,y+b,c) for a,b,c in
				[(-2,0,z0), (-1,-1,z1), (0,-2,z2), (1,-1,z3), (2,0,z4),
				 (-2,0,z),(0,-2,z),(2,0,z),(0,2,z)]]
			leftps = t0, b0, b1, b2, t1
			rightps = t1, b2, b3, b4, t2
			topps = t0, t1, t2, t3

		if not self.landing_hack:
			pygame.draw.polygon(screen, (0,100,100), leftps)   # left panel
			pygame.draw.polygon(screen, (0,50,50), rightps)    # right panel
			pygame.draw.polygon(screen, (0,70,70), topps)      # top panel

	def renderhealthbar(self, surf, looker=None):
		looker = looker or camera
		px, py = looker.screenpos(self.x, self.y, self.z)
		py -= self.healthbarheight
		px -= self.hp0 + 1
		pygame.draw.rect(surf, (200,200,200), (px, py, self.hp0*2+2, 6))
		pygame.draw.rect(surf, (100,0,0), (px+1, py+1, self.hp0*2, 4))
		if self.hp > 0:
			pygame.draw.rect(surf, (0,255,0), (px+1, py+1, self.hp*2, 4))

	def render(self, screen, looker=None):
		looker = looker or camera
		px, py = looker.screenpos(self.x, self.y, self.z)
		if not looker.isvisible(px, py, 100):
			return
		self.renderplatform(screen, looker)
		path = "buildings/selection/%s.png" if self.selected else "buildings/%s.png"
		if self.flashdamage:
			if self.flashdamage % 2:
				path = "buildings/damage/%s.png"
			self.flashdamage -= 1
		img = images.get_image(path % self.btype)
		ix, iy = img.get_size()
		y = py-iy+ix//4
		screen.blit(img, (px-ix//2, y))
		self.last_render_y = y
		if self.hp < self.hp0:
			self.renderhealthbar(screen, looker)

	# Draw onto the minimap
	def drawmini(self, surf, x0, y0):
		px, py = int((self.x - x0)//1), int((-self.y + y0)//1)
		pygame.draw.line(surf, self.minicolor, (px-1,py), (px+1,py))
		pygame.draw.line(surf, self.minicolor, (px,py-1), (px,py+1))


	def update(self, scene):
		pass

	def hurt(self, dhp):
		self.hp = max(self.hp - dhp, 0)
		self.flashdamage = 5 
	
	def heal(self, dhp):
		self.hp = min(self.hp + dhp, self.hp0)
	
	def healfull(self):
		self.hp = self.hp0

	def handleintruders(self, intruders):
		pass
	
	
	def setheight(self, height):
		if self.size == 1:
			ps = (-1,0),(0,-1),(1,0),(0,1)
		elif self.size == 2:
			ps = (-2,0),(-1,-1),(0,-2),(1,-1),(2,0),(1,1),(0,2),(-1,1)
		self.z = max(terrain.iheight(self.x+ax, self.y+ay) for ax, ay in ps) + height

class Drill(Structure):
	btype = "drill"
class Foundry(Structure):
	btype = "foundry"
class Beacon(Structure):
	btype = "beacon"
	attackable = True
	hp0 = 3
	sparkt = 0
	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)
#		self.hq = ....
	def update(self, scene):
		self.sparkt += 1
		if self.sparkt >= 10:
			self.sparkt = 0
#			hq = self.hq
#			effects.add(effects.Spark(self.x, self.y, self.z + 20, hq.x, hq.y, hq.z + 2)

class MachineryLab(Structure):
	btype = "machinerylab"
class ScienceLab(Structure):
	btype = "sciencelab"
class LaunchSite(Structure):
	btype = "launchsite"
	size = 2
class Farm(Structure):
	btype = "farm"
	size = 2
class Greenhouse(Structure):
	btype = "greenhouse"
class HQ(Structure):
	btype = "hq"
	hp0 = 10
	attackable = True
class MedicalTent(Structure):
	btype = "medicaltent"
class Quarry(Structure):
	btype = "quarry"
	size = 2
class Radar(Structure):
	btype = "radar"
class Turret(Structure):
	btype = "turret"
	hp0 = 5
	attackable = True
	healthbarheight = 40
	chargetime = 30
	strength = 1
	shootrange = 4
	t = 0

	def addeffect(self, target):
		# TODO: also a small gunshot effect at the top of the turret
		effects.add(effects.Gunshot(self.x, self.y, self.z + 22, target.x, target.y, target.z + 2))

	def attack(self, target):
		target.hurt(self.strength)
		self.t = 0
		self.addeffect(target)

	def handleintruders(self, intruders):
		self.t += 1
		if self.t >= self.chargetime and intruders and self.hp > 0:
			# Always fire at the nearest intruder
			target = min(intruders, key = lambda i: (i.x-self.x)**2 + (i.y-self.y)**2)
			if (target.x - self.x) ** 2 + (target.y - self.y) ** 2 < self.shootrange ** 2:
				self.attack(target)
# Actually I'm making this into a tractor turret.
class FireTurret(Turret):
	btype = "fireturret"
	h = 24
	targetlimit = 2
	def __init__(self, *args, **kw):
		Turret.__init__(self, *args, **kw)
		self.targets = []
	def addeffect(self, target):
		self.targets.append(target)
		target.addtractor(self)
		effects.add(effects.Tractor(self, target))
	def update(self, scene):
		for target in list(self.targets):
			dx, dy = target.x - self.x, target.y - self.y
			if dx**2 + dy**2 > self.shootrange**2 or not target.alive or self.hp <= 0:
				target.removetractor(self)
				self.targets.remove(target)
	def handleintruders(self, intruders):
		if len(self.targets) >= self.targetlimit:
			return
		Turret.handleintruders(self, intruders)
	def hurt(self, dhp):
		Turret.hurt(self, dhp)
		if self.hp <= 0:
			for target in self.targets:
				target.removetractor(self)

class LazorTurret(Turret):
	btype = "lazorturret"
	strength = 1
	chargetime = 10
	def addeffect(self, target):
		effects.add(effects.LaserBeam(self.x, self.y, self.z + 22, target.x, target.y, target.z + 2))

class TeslaTurret(Turret):
	btype = "teslaturret"
	splashrange = 3

	def addeffect(self, target):
		effects.add(effects.LightningBolt(self.x, self.y, self.z + 22, target.x, target.y, target.z + 2, self.splashrange))

	def attack(self, target, collaterals):
		self.t = 0
		target.hurt(self.strength)
		for i in collaterals:
			i.hurt(self.strength)
		self.addeffect(target)

	def handleintruders(self, intruders):
		self.t += 1
		if self.t >= self.chargetime and intruders and self.hp > 0:
			# fire at whatever will cause the most splash damage
			targets = [i for i in intruders if (i.x-self.x)**2 + (i.y-self.y)**2 < self.shootrange ** 2]
			if not targets: return
			tcs = [(target, [i for i in intruders
				if (i.x-target.x)**2 + (i.y-target.y)**2 < self.splashrange**2])
				for target in targets]
			target, collaterals = max(tcs, key = lambda tc: len(tc[1]))
			self.attack(target, collaterals)

class Resevoir(Structure):
	btype = "resevoir"
	size = 2

def create(user_id, type, x, y):
	output = None
	if type == 'farm': output = Farm(user_id, x, y)
	elif type == 'greenhouse': output = Greenhouse(user_id, x, y)
	elif type == 'hq': output = HQ(user_id, x, y)
	elif type == 'medicaltent': output = MedicalTent(user_id, x, y)
	elif type == 'quarry': output = Quarry(user_id, x, y)
	elif type == 'beacon': output = Beacon(user_id, x, y)
	elif type == 'fireturret': output = FireTurret(user_id, x, y)
	elif type == 'drill': output = Drill(user_id, x, y)
	elif type == 'quarry': output = Quarry(user_id, x, y)
	elif type == 'foundry': output = Foundry(user_id, x, y)
	elif type == 'machinerylab': output = MachineryLab(user_id, x, y)
	elif type == 'teslaturret': output = TeslaTurret(user_id, x, y)
	elif type == 'lazorturret': output = LazorTurret(user_id, x, y)
	elif type == 'sciencelab': output = ScienceLab(user_id, x, y)
	elif type == 'launchsite': output = LaunchSite(user_id, x, y)
	elif type == 'radar': output = Radar(user_id, x, y)
	elif type == 'turret': output = Turret(user_id, x, y)
	elif type == 'resevoir': output = Resevoir(user_id, x, y)
	
	# hideous, but I can type it fast
	if output != None:
		output.type = type
	return output

LANDING_ERA = "landing"
LOWTECH_ERA = "lowtech"
MEDTECH_ERA = "medtech"
HIGHTECH_ERA = "hightech"
SPACE_ERA = "space"

_structure_info = [
	# columns:
	# - type
	# - era
	# - required structures
	# - limit
	# - food
	# - water
	# - aluminum
	# - copper
	# - silicon
	# - oil
	# - formatted description
	# - long description
	# - size
	['hq',             None,         1, [],              0, 0, 0, 0, 0, 0, 0,     "Headquarters",            "stores your precious ship plans"],
	
	['greenhouse',     LANDING_ERA,  1, [],              2, 0, 10, 0, 0, 0, 0,    "Green House",             "Yay. Kale."],
	['medicaltent',    LANDING_ERA,  1, [],              1, 25, 50, 0, 0, 0, 0,   "Medical Tent",            "Fixes papercuts and heartburn"],
	['turret',         LANDING_ERA,  1, [],              3, 0, 0, 0, 0, 0, 0,     "Turret",                  "Bang bang!"],
	['beacon',         LANDING_ERA,  1, [],              3, 0, 0, 0, 0, 0, 0,     "Beacon",                  "Bang bang!"],
	
	['farm',           LOWTECH_ERA,  2, [],              0, 0, 50, 25, 0, 0, 0,   "Farm",                    "beans and carrots, oh my"],
	['drill',          LOWTECH_ERA,  1, [],              0, 0, 25, 200, 0, 0, 0,  "Drill",                   "Produces stone"],
	['quarry',         LOWTECH_ERA,  2, [],              0, 0, 25, 200, 0, 0, 0,  "Quarry",                  "Produces stone"],
	['resevoir',       LOWTECH_ERA,  2, [],              0, 0, 300, 100, 0, 0, 0, "Resevoir",                "Produces more usable water"],
	['fireturret',     LOWTECH_ERA,  1, [],              0, 0, 300, 100, 0, 0, 0, "Fire Turret",             "Produces more usable water"],
	['foundry',        LOWTECH_ERA,  1, [],              0, 0, 25, 200, 0, 0, 0,  "Foundry",                 "Produces stone"],
	
	
	['radar',          MEDTECH_ERA,  1, [],              0, 0, 0, 300, 0, 0, 0,   "Radar",                   "Detects your closest neighbors"],
	['machinerylab',   MEDTECH_ERA,  1, [],              0, 0, 0, 300, 0, 0, 0,   "Machinery Lab",           "Detects your closest neighbors"],
	['teslaturret',    MEDTECH_ERA,  1, [],              0, 0, 0, 300, 0, 0, 0,   "Tesla Turret",            "Detects your closest neighbors"],
	
	['lazorturret',    HIGHTECH_ERA, 1, [],              0, 0, 0, 300, 0, 0, 0,   "Lazor Turret",            "Detects your closest neighbors"],
	['sciencelab',     HIGHTECH_ERA, 1, [],              0, 0, 0, 300, 0, 0, 0,   "Science Lab",             "Detects your closest neighbors"],
	
	['launchsite',     SPACE_ERA,    2, [],              0, 0, 0, 300, 0, 0, 0,   "Launch Site",             "Detects your closest neighbors"]
]

for i in range(len(_structure_info)):
	row = _structure_info[i]
	key = row[0]
	
	j = 0
	while j < 6:
		row[j + 4] = settings.building_cost[key][j]
		j += 1

def get_structure_name(id):
	return _structure_by_id[id][-2]
def get_structure_description(id):
	return _structure_by_id[id][-1]
def get_structure_resources(id):
	s = _structure_by_id[id]
	return {
		'food': s[4],
		'water': s[5],
		'aluminum': s[6],
		'copper': s[7],
		'silicon': s[8],
		'oil': s[9]
	}
_structure_by_era = {}
_structure_by_id = {}
for structure in _structure_info:
	key = structure[1]
	if _structure_by_era.get(key) == None:
		_structure_by_era[key] = []
	_structure_by_era[key].append(structure)
	_structure_by_id[structure[0]] = structure

def get_eras():
	return _structure_by_era

def get_era_formatted_name(shortname):
	if shortname == LANDING_ERA: return "Landing Equipment"
	if shortname == AGRICULTURE_ERA: return "Agriculture"
	return '????'

def get_structure_by_id(id):
	return _structure_by_id[id]


def get_structure_size(type):
	return _structure_by_id[type][2]
