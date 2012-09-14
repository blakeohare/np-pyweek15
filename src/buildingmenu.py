from src.menus import *
from src import network, structure, settings
from src.font import get_tiny_text
import math

def abs(x):
	if x < 0: return -x
	return x

class BuildingMenu(UiScene):
	def __init__(self, playscene, building):
		UiScene.__init__(self)
		self.user_id = playscene.user_id
		self.building = building
		self.playscene = playscene
		bg = pygame.Surface((200, 180)).convert_alpha()
		bg.fill((0, 0, 0, 180))
		self.add_element(Image(100, 60, bg))
		self.initialized = False
		self.hovering = -1
		self.hover_regions = []
		
		top = 65
		left = 105
		bottom = 240 - 5
		right = 295
		if building.btype == 'hq': 
			self.init_hq(playscene, left, top, right, bottom)
	
	def init_hq(self, playscene, left, top, right, bottom):
		y = top
		title = get_text("Headquarters", (255, 255, 255), 24)
		y += 5
		self.add_element(Image(left, y, title))
		y += 5 + title.get_height()
		text = get_tiny_text("Research available:")
		self.add_element(Image(left, y, text))
		y += 5 + text.get_height()
		buildings = playscene.potato.buildings_to_research()[:4]
		for building in buildings:
			x = left
			icon = playscene.toolbar.buttons['build_' + building[0]]
			self.add_element(Image(x, y, icon))
			x += icon.get_width() + 7
			img = get_tiny_text(structure.get_structure_name(building[0]))
			self.add_element(Image(x, y + 5, img))
			self.hover_regions.append((building[0], left, y, right, y + icon.get_height()))
			y += icon.get_height() + 3
		
		self.add_element(Image(left, y + 5, get_tiny_text(
			"Research will cause a mainframe reboot")))
		self.add_element(Image(left, y + 5 + 10, get_tiny_text(
			"which lowers your shields during time.")))
		
			
		
		self.add_element(Button(left, bottom - 17, "Cancel", self.dismiss, True))
		
	
	def press_hover_region(self, arg):
		print (arg)
	
	def dismiss(self):
		self.next = self.playscene
		self.playscene.next = self.playscene
	
	def process_input(self, events, pressed):
		UiScene.process_input(self, events, pressed)
		for event in events:
			if event.type == 'key':
				if event.action == 'back' or event.action == 'action':
					if event.down:
						self.dismiss()
						break
			elif event.type == 'mousemove':
				self.hovering = -1
				i = 0
				while i < len(self.hover_regions):
					hr = self.hover_regions[i]
					if hr[1] < event.x and hr[2] < event.y and hr[3] > event.x and hr[4] > event.y:
						self.hovering = i
					i += 1
			elif event.type == 'mouseleft':
				if event.down:
					if self.hovering != -1:
						self.press_hover_region(self.hover_regions[self.hovering][0])
	
	def update(self):
		UiScene.update(self)
		self.playscene.update()
		
		if self.initialized == False:
			if self.building.btype == 'radar':
				x, y = self.building.getModelXY()
				self.radar_signal = network.send_radar(self.user_id, self.playscene.password, int(x), int(y))
				self.rx = x
				self.ry = y
			self.initialized = True
	
	def render_hq(self, screen):
		pass
	
	def render_radar(self, screen):
		if self.radar_signal != None and self.radar_signal.has_response():
			signal = self.radar_signal.get_response()
			if signal != None and signal.get('success', False):
				data = signal.get('neighbors', [])
				rows = []
				for datum in data:
					
					user = datum[0]
					dx = datum[1] - self.rx
					dy = datum[2] - self.ry
					distance = (dx * dx + dy * dy) ** .5
					if distance == 0: distance = 1 # don't know why this would happen
					distance = int(distance / 6) / 10.0
					direction = '-'
					
					angle = math.atan2(dy, dx) / (2 * 3.14159)
					
					
					angle = int(angle * 2 * 7.9999999)
					# my head hurts
					directions = {
						0 : "Southeast",
						1 : "South",
						2 : "South",
						3 : "Southwest",
						4 : "Southwest",
						5 : "West",
						6 : "West",
						7 : "Northwest",
						-1 : "East",
						-2 : "East",
						-3 : "Northeast",
						-4 : "Northeast",
						-5 : "North",
						-6 : "North",
						-7 : "Northwest"
					}
					direction = directions.get(angle, "")
					rows.append(get_text(str(user) + " " + str(distance) + " km " + direction, (255, 255, 255), 14)) 
				
				y = 105
				x = 100
				for row in rows:
					screen.blit(row, (x, y))
					y += row.get_height() + 5
				
			else:
				text = "Radar is broken right now. Might be the clouds."
				if signal != None:
					text = signal.get('message', text)
				img = get_text(text, (255, 0, 0), 18)
				screen.blit(img, (screen.get_width() // 2 - img.get_width() // 2, screen.get_height() // 2 - img.get_height() // 2))
		else:
			img = get_text("Scanning...", (255, 255, 255), 18)
			screen.blit(img, (screen.get_width() // 2 - img.get_width() // 2, screen.get_height() // 2 - img.get_height() // 2))

	
	def render(self, screen):
		self.playscene.render(screen)
		UiScene.render(self, screen)
		
		if self.building.btype == 'radar':
			self.render_radar(screen)
		elif self.building.btype == 'hq':
			self.render_hq(screen)
		
		i = 0
		while i < len(self.hover_regions):
			hr = self.hover_regions[i]
			r = pygame.Rect(hr[1], hr[2], hr[3] - hr[1], hr[4] - hr[2])
			color = (80, 80, 80)
			if self.hovering == i:
				color = (0, 128, 255)
			pygame.draw.rect(screen, color, r, 1)
			i += 1