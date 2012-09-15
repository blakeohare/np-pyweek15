import pygame
import random
import os
from src import settings

_current = None


playlist = [
	'groovycolony',
	'latincolony',
	'groovycolony']

normalizer = {
	'title': .1
}

initialized = False
audible = True

def play_this(name, loop):
	if not settings.playmusic:
		return
	pygame.mixer.music.load(os.path.join('media', 'music', name + '.ogg'))
	pygame.mixer.music.play(-1 if loop else 0)

def ensure_playing(song):
	global initialized, _current, audible
	
	if not settings.playmusic:
		return
	
	naudible = song != None
	
	toggle_audibility = naudible != audible
	audible = naudible
	
	if toggle_audibility and not audible:
		pygame.mixer.music.set_volume(0)
	
	
	
	if not initialized:
		initialized = True
		pygame.mixer.music.set_endevent(pygame.USEREVENT)
	
	
	if song != None and song != _current:
		_current = song
		if song == 'general':
			play_this(playlist[0], False)
			shuffle_playlist()
		else:
			play_this(song, True)

	if toggle_audibility and audible:
		pygame.mixer.music.set_volume(normalizer.get(song, 1.0))
	
def shuffle_playlist():
	playlist.append(playlist.pop(0))

def song_ended():
	global _current
	_current = None

sounds = {}
def play_sound(name, subdir="SFX"):
	if not settings.playsfx:
		return
	key = name, subdir
	if key not in sounds:
		fname = os.path.join("media", subdir, name + ".ogg")
		if os.path.exists(fname):
			sounds[key] = pygame.mixer.Sound(fname)
		else:
			print("Unable to load sound %s" % fname)
			sounds[key] = None
	if sounds[key]:
		sounds[key].play()

def play_voice(name):
	play_sound(name, "voice")



