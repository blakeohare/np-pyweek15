from src.menus import *
from src.images import get_image
from src import playscene
from src import util
from src import slideshows
from src import tutorial
from src import scenefactory
from src import jukebox

class TitleScene(UiScene):
	def __init__(self):
		UiScene.__init__(self)
		self.username = TextBox(20, 200, 100, "Username")
		self.add_element(Image(0, 0, get_image('backgrounds/title.png')))
		self.add_element(self.username)
		self.button = Button(20, 230, "Login", self.login_pressed, False)
		self.add_element(self.button)
		self.add_element(Button(300, 200, "Story", self.story_pressed, True))
		self.add_element(Button(300, 230, "Tutorial Mode", self.tutorial_pressed, True))
		self.add_element(Button(300, 260, "Credits", self.credits_pressed, True))
		self.auth_request = None
	
	def story_pressed(self):
		self.next = slideshows.StoryScene()
	
	def tutorial_pressed(self):
		self.next = playscene.LoadingScene(
			1, "11111111111111111111111111111111", '0^0', '30^30', False, 50, [], False, [0, 0, 0], True)
	
	def credits_pressed(self):
		self.next = slideshows.CreditsScene()
	
	def update(self):
		UiScene.update(self)
		jukebox.ensure_playing('title')
		if len(self.username.text) == 0:
			self.button.disable()
		else:
			self.button.enable()
		
		if self.auth_request != None and self.auth_request.has_response():
			response = self.auth_request.get_response()
			if not response.get('success', False):
				response.get('message', "Server made an unrecognized response")
			else:
				hq = response.get('hq')
				sector = hq[0]
				loc = hq[1]
				user_id = response.get('user_id', 0)
				is_new = response.get('is_new', False)
				research = response.get('research', 0)
				buildings = response.get('buildings', [])
				unlock = self.username.text.endswith('!')
				bots = response.get('bots', [0, 0, 0])
				self.next = playscene.LoadingScene(user_id, self.password, sector, loc, is_new, research, buildings, unlock, bots, False)
			self.auth_request = None
	
	def login_pressed(self):
		raw_users = util.read_file('users.txt')
		if raw_users == None:
			users = []
			raw_users = ''
		else:
			users = util.trim(raw_users).split('\n')
		user_lookup = {}
		for user in users:
			name = util.alphanums(util.trim(user[32:]))
			password = user[:32].lower()
			user_lookup[name] = password
		
		user = util.alphanums(self.username.text)
		password = user_lookup.get(user, None)
		if password == None:
			password = util.md5(str(time.time()) + "leprechauns")
			raw_users += "\n" + password + user
			util.write_file('users.txt', raw_users)
		self.auth_request = network.send_authenticate(user, password)
		self.password = password
	
	def process_input(self, events, pressed_keys):
		if pressed_keys['debug']:
			from src import play
			self.next = play.PlayScene()
		UiScene.process_input(self, events, pressed_keys)

scenefactory.add_builder('title', lambda:TitleScene())