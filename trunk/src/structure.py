import pygame
from src import camera, images, terrain

class Structure(object):
	# TODO: handle buildings with bigger footprints than 1x1
	def __init__(self, user_id, x, y, z=None):
		self.user_id = user_id
		self.x, self.y = terrain.toRender(x, y)
		self.z = terrain.iheight(x, y) if z is None else z
    
	def renderplatform(self, screen):
		# TODO: this should probably be cached into an image
		x, y = self.x, self.y
		z0, z1, z2, z3 = terrain.ihcorners(x, y)
		zm = max((z0, z1, z2, z3))
		p0,p1,p2,p3,p4,p5,p6 = [camera.screenpos(a,b,c) for a,b,c in
				((x-1,y,zm), (x,y-1,zm), (x+1,y,zm), (x,y+1,zm), (x-1,y,z0), (x,y-1,z1), (x+1,y,z2))]
		# left
		pygame.draw.polygon(screen, (0,100,100), (p0,p4,p5,p1))
		# right
		pygame.draw.polygon(screen, (0,50,50), (p1,p5,p6,p2))
		# top
		pygame.draw.polygon(screen, (0,70,70), (p0,p1,p2,p3))
    
	def render(self, screen):
		px, py = camera.screenpos(self.x, self.y, self.z)
		if not camera.isvisible(px, py, 100):
			return
		self.renderplatform(screen)
		img = images.get_image("buildings/%s.png" % self.btype)
		ix, iy = img.get_size()
		screen.blit(img, (px-ix//2, py-iy+ix//4))

	def update(self):
		pass

class Farm(Structure):
	btype = "farm"
class Greenhouse(Structure):
	btype = "greenhouse"
class HQ(Structure):
	btype = "hq"
class MedicalTent(Structure):
	btype = "medicaltent"
class Quarry(Structure):
	btype = "quarry"
class Radar(Structure):
	btype = "radar"
class Turret(Structure):
	btype = "turret"
class WaterTreatment(Structure):
	btype = "watertreatment"

def create(user_id, type, x, y):
	if type == 'farm': return Farm(user_id, x, y)
	if type == 'greenhouse': return Greenhouse(user_id, x, y)
	if type == 'hq': return HQ(user_id, x, y)
	if type == 'medicaltent': return MedicalTent(user_id, x, y)
	if type == 'quarry': return Quarry(user_id, x, y)
	if type == 'radar': return Radar(user_id, x, y)
	if type == 'turret': return Turret(user_id, x, y)
	if type == 'watertreatment': return WaterTreatment(user_id, x, y)
	return None

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
	['farm', AGRICULTURAL, ['medicaltent'], 0, 0, 50, 25, "Farm", "beans and carrots, oh my"],
	['greenhouse', LANDING_ERA, [], 2, 0, 10, 0, "Green House", "Yay. Kale."],
	['hq', None, [], 0, 0, 0, "Headquarters", "stores your precious ship plans"],
	['medicaltent', LANDING_ERA, [], 1, 25, 50, 0, "Medical Tent", "Fixes papercuts and heartburn"],
	['quarry', AGRICULTURAL, ['medicaltent'], 0, 0, 25, 200, "Quarry", "Produces stone"],
	['turret', LANDING_ERA, [], 3, 0, 0, 0, "Turret", "Bang bang!"],
	['watertreatment', AGRICULTURAL, ['medicaltent'], 0, 0, 300, 100, "Water Treament Facility", "Produces more usable water"]
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
