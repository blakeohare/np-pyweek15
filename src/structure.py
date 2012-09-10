import pygame
from src import worldmap, camera, images

class Structure(object):
	# TODO: handle buildings with bigger footprints than 1x1
	def __init__(self, user_id, x, y, z=None):
		self.user_id = user_id
		self.x, self.y = worldmap.toRender(x, y)
		self.z = worldmap.iheight(x, y) if z is None else z
    
	def renderplatform(self, screen):
		# TODO: this should probably be cached into an image
		x, y = self.x, self.y
		z0, z1, z2, z3 = worldmap.ihcorners(x, y)
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

LANDING_ERA = "Landing"
AGRICULTURAL = "Agricultural"

_structure_info = [
	# columns:
	# - type
	# - era
	# - required structures
	# - limit
	# - food
	# - water
	# - minerals
	['farm', AGRICULTURAL, ['medicaltent'], 0, 0, 50, 25],
	['greenhouse', LANDING_ERA, [], 2, 0, 10, 0],
	['hq', None, [], 0, 0, 0],
	['medicaltent', LANDING_ERA, [], 1, 25, 50, 0],
	['quarry', AGRICULTURAL, ['medicaltent'], 0, 0, 25, 200],
	['turret', LANDING_ERA, [], 3, 0, 0, 0],
	['watertreatment', AGRICULTURAL, ['medicaltent'], 0, 0, 300, 100]
]

_structure_by_era = {}
for structure in _structure_info:
	key = structure[1]
	if _structure_by_era.get(key) == None:
		_structure_by_era[key] = []
	_structure_by_era[key].append(structure)

def get_eras():
	return _structure_by_era
