import urllib
import threading

class Request(threading.Thread):
	def __init__(self, action, args, user, password):
		threading.Thread.__init__(self)
		self.args = {'action': action}
		if user != None:
			self.args['user'] = user
		if password != None:
			self.args['password'] = password
		for key in args:
			self.args[key] = args[key]
		self.hasresponse = False
		self.response = None
		self.error = False
		self.lock = threading.Lock()
		
	def run(self):
		is_error = False
		data = None
		try:
			url = 'http://pyweek15.nfshost.com/server.py?' + urllib.urlencode(self.args)
			print("Sending: " + url)
			c = urllib.urlopen(url)
			data = c.read()
			c.close()
			
		except:
			is_error = True
		
		self.lock.acquire(True)
		self.error = is_error
		self.response = data
		self.hasresponse = True
		self.lock.release()
		
	
	def has_response(self):
		return self.hasresponse
	
	def get_response(self):
		try:
			return deserialize_thing(self.response)
		except:
			return { 'success': False, 'message': "unknown server response: " + str(self.response) }
	
	def is_error(self):
		return self.error
	
	def send(self):
		self.start()

def _send_command(action, args, user=None, password=None):
	request = Request(action, args, user, password)
	request.send()
	return request

def read_till_bang(stream, index):
	output = []
	while index[0] < len(stream) and stream[index[0]] != '!':
		c = stream[index[0]]
		if c == '$':
			index[0] += 1
			c = stream[index[0]]
			if c == '$':
				output.append('$')
			else:
				output.append('!')
		else:
			output.append(c)
		index[0] += 1
	index[0] += 1
	return ''.join(output)

def deserialize_thing(string, index=[0]):
	if index[0] >= len(string): return None
	t = string[index[0]]
	index[0] += 1
	if t == 'n':
		index[0] += 1
		return None
	if t in 'ilfsb':
		x = read_till_bang(string, index)
		if t == 'i': return int(x)
		if t == 'l': return long(x)
		if t == 'f': return float(x)
		if t == 's': return x
		if t == 'b': return x == '1'
	if t == 't':
		output = []
		while index[0] < len(string) and string[index[0]] != '!':
			output.append(deserialize_thing(string, index))
		index[0] += 1
		return output
	
	if t == 'd':
		output = {}
		while index[0] < len(string) and string[index[0]] != '!':
			key = deserialize_thing(string, index)
			value = deserialize_thing(string, index)
			output[key] = value
		index[0] += 1
		return output
	index[0] += 1
	return None

def send_echo(stuff):
	return _send_command("echo", { 'data': stuff })

def send_authenticate(username, password):
	return _send_command('authenticate', {}, username, password)