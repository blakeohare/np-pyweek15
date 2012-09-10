from src import util
from src import network
from src import worldmap
from src.font import get_text
from src import sprite
from src import structure
from src import camera
from src import data
from src import settings

class LoadingScene:
	def __init__(self, user_id, password, sector, loc, new):
		self.next = self
		self.user_id = user_id
		self.password = password
		self.counter = 0
		self.new = new
		self.sector = sector
		self.loc = loc
		self.poll = network.send_poll(user_id, password, [sector], {})
		self.potato = data.MagicPotato()
		self.loading_x = 200 - get_text("Loading..", (255, 255, 255), 22).get_width() // 2
	
	def process_input(self, events, pressed):
		pass
	
	def update(self):
		if self.poll.has_response():
			response = self.poll.get_response()
			if response.get('success', False):
				self.potato.apply_poll_data(response)
				self.poll = None
				self.next = PlayScene(self.user_id, self.password, self.potato, util.totuple(self.sector), util.totuple(self.loc), self.new)
			else:
				print("Something terrible has happened.")
				self.next = None
	
	def render(self, screen):
		self.counter += 1
		z = (self.counter // 15) % 4
		loading = get_text("Loading" + ("." * z), (255, 255, 255), 22)
		screen.fill((0, 0, 0))
		screen.blit(loading, (self.loading_x, 100))
		
class PlayScene:
	def __init__(self, user_id, password, potato, starting_sector, starting_xy, show_landing_sequence):
		self.potato = potato
		self.user_id = user_id
		self.password = password
		self.next = self
		self.hq = None
		self.show_landing_sequence = show_landing_sequence
		self.cx = starting_sector[0] * 60 + starting_xy[0]
		self.cy = starting_sector[1] * 60 + starting_xy[1]
		self.player = sprite.You(self.cx, self.cy + 1)
		self.sprites = [self.player]
		self.poll_countdown = 0
		self.poll = None
	
	def process_input(self, events, pressed):
		direction = ''
		dx, dy = 0, 0
		v = .1
		if pressed['up']: dy += v
		if pressed['down']: dy -= v
		if pressed['left']: dx -= v
		if pressed['right']: dx += v
		
		self.player.x += dx
		self.player.y += dy
		
	def update(self):
		self.potato.update()
		self.player.update()
		self.poll_countdown -= 1
		if self.poll_countdown < 0 and self.poll == None:
			nearby = []
			xy = self.player.getModelXY()
			sector = (int(xy[0] // 60), int(xy[1] // 60))
			self.poll = network.send_poll(
				self.user_id, self.password,
				[sector],
				self.potato.last_id_by_sector)
		
		if self.poll != None and self.poll.has_response():
			self.potato.apply_poll_data(self.poll.get_response())
			self.poll = None
			self.poll_countdown = 10 * settings.fps
			
		
	def render(self, screen):
		cx = self.player.x
		cy = self.player.y
		camera.lookat(cx, cy)
		#print cx, cy, self.player.getModelXY()
		# TODO: Ask Cosmo about the cursor crashing
		structures = self.potato.get_structures_for_screen(cx, cy)
		labels = []
		for structure in structures:
			if structure.btype == 'hq':
				owner_id = structure.user_id
				name = self.potato.get_user_name(owner_id)
				img = get_text(name, (255, 255, 255), 18)
				labels.append([
					img,
					(structure.x - cx) * 16 + 200 - img.get_width() // 2,
					(-structure.y + cy) * 8 + 150 + 40])
		worldmap.drawscene(screen, self.sprites + structures)#, (int(cx), int(cy)))
		for label in labels:
			screen.blit(label[0], (label[1], label[2]))
		mx,my = self.player.getModelXY()
		mx = int(mx)
		my = int(my)
		coords = get_text("R: " + str((int(cx), int(cy))) + " M: " + str((mx, my)), (255, 255, 0), 18)
		screen.blit(coords, (5, screen.get_height() - 5 - coords.get_height()))