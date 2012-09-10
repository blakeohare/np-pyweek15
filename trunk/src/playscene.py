from src import util
from src import network
from src import worldmap
from src.font import get_text
from src import sprite
from src import structure
from src import camera
from src import data

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
	
	def process_input(self, events, pressed):
		pass
	
	def update(self):
		if self.poll.has_response():
			response = self.poll.get_response()
			if response.get('success', False):
				self.potato.apply_poll_data(response)
				self.poll = None
				self.next = PlayScene(self.potato, util.totuple(self.sector), util.totuple(self.loc), self.new)
			else:
				print("Something terrible has happened")
				self.next = None
	
	def render(self, screen):
		self.counter += 1
		z = (self.counter // 15) % 4
		loading = get_text("Loading" + ("." * z), (255, 255, 255), 22)
		screen.fill((0, 0, 0))
		screen.blit(loading, (200 - loading.get_width() // 2, 100))
		
class PlayScene:
	def __init__(self, potato, starting_sector, starting_xy, show_landing_sequence):
		self.potato = potato
		self.next = self
		self.hq = None
		self.show_landing_sequence = show_landing_sequence
		self.cx = starting_sector[0] * 60 + starting_xy[0]
		self.cy = starting_sector[1] * 60 + starting_xy[1]
		self.player = sprite.You(self.cx, self.cy + 1)
		self.sprites = [self.player]
	
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
		self.player.update()
		
	def render(self, screen):
		cx = self.player.x
		cy = self.player.y
		camera.lookat(cx, cy)
		#print cx, cy, self.player.getModelXY()
		# TODO: Ask Cosmo about the cursor crashing
		worldmap.drawscene(screen, self.sprites + self.potato.get_structures_for_screen(cx, cy))#, (int(cx), int(cy)))
		