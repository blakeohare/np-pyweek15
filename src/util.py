import os
import hashlib
import time
from src import settings

# a dirty/stupid way to do it but it doesn't need to be fast
def trim(string):
	while len(string) > 0 and string[0] in ' \r\n\t':
		string = string[1:]
	while len(string) > 0 and string[-1] in ' \r\n\t':
		string = string[:-1]
	return string


def md5(thing):
	thing = str(thing).encode('utf-8')
	return hashlib.md5(thing).hexdigest()

def read_file(path):
	if os.path.exists(path):
		c = open(path, 'rt')
		text = c.read()
		c.close()
		return text
	return None

def write_file(path, contents):
	c = open(path, 'wt')
	c.write(contents)
	c.close()

def totuple(stringpair):
	x,y = stringpair.split('^')
	return (int(x), int(y))

def fromtuple(t):
	return str(t[0]) + '^' + str(t[1])

def floor(n):
	if n < 0:
		if int(n) == n: return int(n)
		return -int(-n) - 1
	return int(n)

_alpha = None
def alphanums(string):
	global _alpha
	if _alpha == None:
		_alpha = {}
		for letter in 'abcdefghijklmnopqrstuvwyxz0123456789':
			_alpha[letter] = letter
			_alpha[letter.upper()] = letter
	
	output = []
	for char in string:
		output.append(_alpha.get(char, ''))
	return ''.join(output)

class Profiler:
	def __init__(self, name):
		self.name = str(name)
		self.start = time.time()
		
	def stop(self):
		diff = int(1000 * (time.time() - self.start))
		verboseprint(self.name + str(diff) + ' ms')

def profile(name):
	return Profiler(name)

def verboseprint(thing):
	if settings.show_verbose_output:
		pass #print(str(thing))
	