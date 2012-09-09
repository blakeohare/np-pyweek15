import os
import hashlib

# a dirty/stupid way to do it but it doesn't need to be fast
def trim(string):
	while len(string) > 0 and string[0] in ' \r\n\t':
		string = string[1:]
	while len(string) > 0 and string[-1] in ' \r\n\t':
		string = string[:-1]
	return string


def md5(thing):
	return hashlib.md5(str(thing)).hexdigest()

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