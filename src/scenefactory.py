builders = {}

def add_builder(key, method):
	builders[key] = method

def build_scene(key, params):
	return builders[key](*params)


