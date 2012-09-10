def format_output(thing, debug):
	if debug:
		return str(thing).replace('\n', '<br />')
	else:
		return serialize_thing(thing)

def serialize_thing(thing):
	if thing == None:
		return serialize_none()
	t = str(type(thing)).split("'")[1]
	if t == 'int':
		return serialize_int(thing)
	if t == 'long':
		return serialize_long(thing)
	if t == 'float':
		return serialize_float(thing)
	if t == 'str':
		return serialize_string(thing)
	if t == 'list' or t == 'tuple':
		return serialize_list(thing)
	if t == 'dict':
		return serialize_dictionary(thing)
	if t == 'bool':
		return serialize_bool(thing)
	return serialize_none()

def serialize_int(thing):
	return 'i' + str(thing) + '!'

def serialize_long(thing):
	return 'l' + str(thing) + '!'

def serialize_float(thing):
	return 'f' + str(thing) + '!'

def serialize_string(thing):
	return 's' + str(thing).replace('$', '$$').replace('!', '$b') + '!'

def serialize_list(thing):
	output = ['t']
	for item in thing:
		output.append(serialize_thing(item))
	output.append('!')
	return ''.join(output)

def serialize_bool(thing):
	return 'b1!' if thing else 'b0!'

def serialize_dictionary(thing):
	output = ['d']
	for key in thing:
		output.append(serialize_string(str(key)))
		output.append(serialize_thing(thing[key]))
	output.append('!')
	return ''.join(output)

def serialize_none(thing):
	return 'n!'

def coord_from_tuple(tup):
	return '%i^%i'%tup

def tuple_from_coord(coord):
	xval,yval=coord.split('^')
	return int(xval), int(yval)

def parseInt(value):
	try:
		return int(value)
	except:
		return 0

def get_structure_size(type):
	if type in ('turret', 'hq'):
		return 1
	return 1

def tsanitize(string):
	return '^'.join(map(lambda x:str(int(x)), string.split('^')))