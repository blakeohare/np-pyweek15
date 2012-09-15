import pygame

_fonts = {}
_text = {}

def get_font(size):
	font = _fonts.get(size)
	if font == None:
		font = pygame.font.SysFont(pygame.font.get_default_font(), size)
		_fonts[size] = font
	return font

def get_text(text, color, size):
	k = (text, color, size)
	img = _text.get(k, None)
	if img == None:
		font = get_font(size)
		img = font.render(text, True, color)
		_text[k] = img
	return img


_letters = {}

def makenblit(col, row, tf):
	img = pygame.Surface((5, 8)).convert_alpha()
	img.fill((0, 0, 0, 0))
	img.blit(tf, (-col * 6, -row * 8))
	return img

_tiny_cache = {}

def get_tiny_text(text):
	img = _tiny_cache.get(text, None)
	if img == None:
		if len(_letters) == 0:
			from src import images
			tf = images.get_image('tinyletters2.png')
			
			_letters['A'] = makenblit(0, 0, tf)
			_letters['B'] = makenblit(1, 0, tf)
			_letters['C'] = makenblit(2, 0, tf)
			_letters['D'] = makenblit(3, 0, tf)
			_letters['E'] = makenblit(4, 0, tf)
			_letters['F'] = makenblit(5, 0, tf)
			_letters['G'] = makenblit(6, 0, tf)
			_letters['H'] = makenblit(7, 0, tf)
			_letters['I'] = makenblit(8, 0, tf)
			_letters['J'] = makenblit(9, 0, tf)
			_letters['K'] = makenblit(10, 0, tf)
			_letters['L'] = makenblit(11, 0, tf)
			_letters['M'] = makenblit(12, 0, tf)
			_letters['N'] = makenblit(0, 1, tf)
			_letters['O'] = makenblit(1, 1, tf)
			_letters['P'] = makenblit(2, 1, tf)
			_letters['Q'] = makenblit(3, 1, tf)
			_letters['R'] = makenblit(4, 1, tf)
			_letters['S'] = makenblit(5, 1, tf)
			_letters['T'] = makenblit(6, 1, tf)
			_letters['U'] = makenblit(7, 1, tf)
			_letters['V'] = makenblit(8, 1, tf)
			_letters['W'] = makenblit(9, 1, tf)
			_letters['X'] = makenblit(10, 1, tf)
			_letters['Y'] = makenblit(11, 1, tf)
			_letters['Z'] = makenblit(12, 1, tf)
			_letters['a'] = makenblit(0, 2, tf)
			_letters['b'] = makenblit(1, 2, tf)
			_letters['c'] = makenblit(2, 2, tf)
			_letters['d'] = makenblit(3, 2, tf)
			_letters['e'] = makenblit(4, 2, tf)
			_letters['f'] = makenblit(5, 2, tf)
			_letters['g'] = makenblit(6, 2, tf)
			_letters['h'] = makenblit(7, 2, tf)
			_letters['i'] = makenblit(8, 2, tf)
			_letters['j'] = makenblit(9, 2, tf)
			_letters['k'] = makenblit(10, 2, tf)
			_letters['l'] = makenblit(11, 2, tf)
			_letters['m'] = makenblit(12, 2, tf)
			_letters['n'] = makenblit(0, 3, tf)
			_letters['o'] = makenblit(1, 3, tf)
			_letters['p'] = makenblit(2, 3, tf)
			_letters['q'] = makenblit(3, 3, tf)
			_letters['r'] = makenblit(4, 3, tf)
			_letters['s'] = makenblit(5, 3, tf)
			_letters['t'] = makenblit(6, 3, tf)
			_letters['u'] = makenblit(7, 3, tf)
			_letters['v'] = makenblit(8, 3, tf)
			_letters['w'] = makenblit(9, 3, tf)
			_letters['x'] = makenblit(10, 3, tf)
			_letters['y'] = makenblit(11, 3, tf)
			_letters['z'] = makenblit(12, 3, tf)
			_letters['1'] = makenblit(0, 4, tf)
			_letters['2'] = makenblit(1, 4, tf)
			_letters['3'] = makenblit(2, 4, tf)
			_letters['4'] = makenblit(3, 4, tf)
			_letters['5'] = makenblit(4, 4, tf)
			_letters['6'] = makenblit(5, 4, tf)
			_letters['7'] = makenblit(6, 4, tf)
			_letters['8'] = makenblit(7, 4, tf)
			_letters['9'] = makenblit(8, 4, tf)
			_letters['0'] = makenblit(9, 4, tf)
			_letters['!'] = makenblit(10, 4, tf)
			_letters['?'] = makenblit(11, 4, tf)
			_letters['.'] = makenblit(12, 4, tf)
			_letters['('] = makenblit(0, 5, tf)
			_letters[')'] = makenblit(1, 5, tf)
			_letters['/'] = makenblit(2, 5, tf)
			_letters[','] = makenblit(3, 5, tf)
			_letters['-'] = makenblit(4, 5, tf)
			_letters["'"] = makenblit(5, 5, tf)
			_letters['"'] = makenblit(6, 5, tf)
			_letters[':'] = makenblit(7, 5, tf)
			_letters['%'] = makenblit(8, 5, tf)
			_letters['&'] = makenblit(9, 5, tf)
			
		output = pygame.Surface((5 * len(text), 8)).convert_alpha()
		output.fill((0, 0, 0, 0))
		x = 0
		for char in text:
			img = _letters.get(char, None)
			if img != None:
				output.blit(img, (x, 0))
			x += 5
		img = output
		_tiny_cache[text] = img
	return img