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
