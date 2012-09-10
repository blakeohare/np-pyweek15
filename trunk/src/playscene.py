from src import util
from src import network
from src import worldmap
from src.font import get_text
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
	
	def process_input(self, events, pressed):
		pass
	
	def update(self):
		if self.poll.has_response():
			response = self.poll.get_response()
			if response.get('success', False):
				self.poll = None
				self.next = PlayScene(self.sector, self.loc, self.new)
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
	def __init__(self, starting_sector, starting_xy, show_landing_sequence):
		self.next = self
		self.hq = None
		self.show_landing_sequence = show_landing_sequence
	
	def process_input(self, events, pressed):
		pass
		
	def update(self):
		pass
		
	def render(self, screen):
		screen.fill((255, 255, 255))
		