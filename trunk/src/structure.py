import pygame
from src import camera, images, terrain, util

class Structure(object):
	minicolor = 192, 192, 192
	size = 1
	# TODO: handle buildings with bigger footprints than 1x1
	def __init__(self, user_id, x, y, z=None):
		self.user_id = user_id
		self.selected = False
		self.x, self.y = terrain.toCenterRender(x, y)
		if self.size == 2: self.y -= 1
		if z is None:
			if self.size == 1:
				ps = (-1,0),(0,-1),(1,0),(0,1)
			elif self.size == 2:
				ps = (-2,0),(-1,-1),(0,-2),(1,-1),(2,0),(1,1),(0,2),(-1,1)
			self.z = max(terrain.iheight(self.x+ax, self.y+ay) for ax, ay in ps)
		else:
			self.z = z
	
	def getModelXY(self):
		return terrain.toModel(self.x, self.y + 1)
		
	def renderplatform(self, screen, looker=None):
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


		pygame.draw.polygon(screen, (0,100,100), leftps)   # left panel
		pygame.draw.polygon(screen, (0,50,50), rightps)    # right panel
		pygame.draw.polygon(screen, (0,70,70), topps)      # top panel

	def render(self, screen, looker=None):
		looker = looker or camera
		px, py = looker.screenpos(self.x, self.y, self.z)
		if not looker.isvisible(px, py, 100):
			return
		self.renderplatform(screen, looker)
		path = "buildings/selection/%s.png" if self.selected else "buildings/%s.png"
		img = images.get_image(path % self.btype)
		ix, iy = img.get_size()
		screen.blit(img, (px-ix//2, py-iy+ix//4))

	# Draw onto the minimap
	def drawmini(self, surf, x0, y0):
		px, py = int((self.x - x0)//1), int((-self.y + y0)//1)
		pygame.draw.line(surf, self.minicolor, (px-1,py), (px+1,py))
		pygame.draw.line(surf, self.minicolor, (px,py-1), (px,py+1))


	def update(self):
		pass

class Farm(Structure):
	btype = "farm"
	size = 2
class Greenhouse(Structure):
	btype = "greenhouse"
class HQ(Structure):
	btype = "hq"
class MedicalTent(Structure):
	btype = "medicaltent"
class Quarry(Structure):
	btype = "quarry"
	size = 2
class Radar(Structure):
	btype = "radar"
class Turret(Structure):
	btype = "turret"
class WaterTreatment(Structure):
	btype = "watertreatment"
	size = 2

def create(user_id, type, x, y):
	output = None
	if type == 'farm': output = Farm(user_id, x, y)
	elif type == 'greenhouse': output = Greenhouse(user_id, x, y)
	elif type == 'hq': output = HQ(user_id, x, y)
	elif type == 'medicaltent': output = MedicalTent(user_id, x, y)
	elif type == 'quarry': output = Quarry(user_id, x, y)
	elif type == 'radar': output = Radar(user_id, x, y)
	elif type == 'turret': output = Turret(user_id, x, y)
	elif type == 'watertreatment': output = WaterTreatment(user_id, x, y)
	
	# hideous, but I can type it fast
	if output != None:
		output.type = type
	return output

LANDING_ERA = "landing"
AGRICULTURAL = "agriculture"

_structure_info = [
	# columns:
	# - type
	# - era
	# - required structures
	# - limit
	# - food
	# - water
	# - minerals
	# - formatted description
	# - long description
	# - size
	['farm',           AGRICULTURAL, ['medicaltent'], 0, 0, 50, 25,   "Farm",                    "beans and carrots, oh my", 2],
	['greenhouse',     LANDING_ERA,  [],              2, 0, 10, 0,    "Green House",             "Yay. Kale.", 1],
	['hq',             None,         [],              0, 0, 0, 0,     "Headquarters",            "stores your precious ship plans", 1],
	['medicaltent',    LANDING_ERA,  [],              1, 25, 50, 0,   "Medical Tent",            "Fixes papercuts and heartburn", 1],
	['quarry',         AGRICULTURAL, ['medicaltent'], 0, 0, 25, 200,  "Quarry",                  "Produces stone", 2],
	['turret',         LANDING_ERA,  [],              3, 0, 0, 0,     "Turret",                  "Bang bang!", 1],
	['watertreatment', AGRICULTURAL, ['medicaltent'], 0, 0, 300, 100, "Water Treament Facility", "Produces more usable water", 2]
]

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
	return _structure_by_id[type][9]
