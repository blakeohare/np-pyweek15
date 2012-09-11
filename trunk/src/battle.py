class Battle:
	def __init__(self, user_id, other_user_id=None):
		# if other_user_id is, then this is an alien vs player session
		self.user_id = user_id
		self.other_id = other_user_id
		
		self.data_stolen = 0.0 # add to this in real time as the sprites successfully get into the HQ
	
	def process_input(self, events, pressed_keys):
		pass
		# I was thinking we could allow panning during battles with the arrow keys
		# or something. Bases can be larger than the available screen
	
	def collective_sprite_midpoint(self):
		return (0, 0)
	
	def update(self):
		pass
	
	# aliens, seeker bots, projectiles
	def get_sprites(self):
		return []
	
	def is_complete(self):
		return False
	##
	# @return {!int} The number of bytes stolen.
	#
	def bytes_stolen(self):
		return self.data_stolen
	
	# This function is done.
	def is_computer_attacking(self):
		return self.other_id == None
	
	# This is used to send deletions to the server.
	# If you return a building in this function, it should not be
	# returned again (like pygame.event.get())
	# actual values are coordinates of the building
	def new_buildings_destroyed(self):
		return []
	
	# return buildings that have been damaged when a player attacks another player
	# this will be 
	# @return a dictionary with coordinate keys. value is ignored 
	def all_buildings_damaged(self):
		return {}