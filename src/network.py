
from src import util

import sys
if sys.version > '3':
	from urllib.request import urlopen
	from urllib.parse import urlencode
else:
	from urllib import urlopen
	from urllib import urlencode
import threading

import time

_server_address = util.read_file('server.txt')

class Request(threading.Thread):
	def __init__(self, action, args, user, password):
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self.args = {'action': action}
		if user != None:
			self.args['user_id'] = user
		if password != None:
			self.args['password'] = password
		for key in args:
			self.args[key] = args[key]
		self.hasresponse = False
		self.response = None
		self.error = False
		self.lock = threading.Lock()
	
	def update_address(self, new_address):
		global _server_address
		_server_address = new_address
		print("SERVER HAS MOVED TO:", new_address)
		util.write_file('server.txt', new_address)
	
	def run(self):
		self.send_request()
	
	def send_request(self, attempts=10):
		is_error = False
		data = None
		try:
			url = _server_address + '/server.py?' + urlencode(self.args)
			print("Sending: " + url)
			c = urlopen(url)
			raw_bytes = c.read()
			if 'bytes' in str(type(raw_bytes)): # Ugh, new Python 3 annoyance I learned just now
				raw_bytes = raw_bytes.decode('utf-8')
			data = deserialize_thing(raw_bytes)
			print("RECEIVED: ", data)
			if data == None:
				print("RAW DATA:", raw_bytes.replace('<br />', "\n"))
			c.close()
			
			if data != None and data.get('redirect') != None:
				self.update_address(str(data['redirect']))
				self.send_request()
				return
			
		except:
			if attempts < 1:
				data = { 'success': False, 'message': "Server did not respond" }
				is_error = True
			else:
				time.sleep((11 - attempts) * 3.0)
				self.send_request(attempts - 1)
				return
		
		self.lock.acquire(True)
		self.error = is_error
		self.response = data
		self.hasresponse = True
		self.lock.release()
		
	
	def has_response(self):
		return self.hasresponse
	
	def get_response(self):
		try:
			return self.response
		except:
			return { 'success': False, 'message': "unknown server response: " + str(self.response) }
	
	def is_error(self):
		return self.error
	
	def get_error(self):
		if self.hasresponse:
			return self.response.get("message", "Unknown error has occurred.")
	
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

def deserialize_thing(string, index=None):
	if index == None:
		index = [0]
	if index[0] >= len(string): return None
	t = string[index[0]]
	index[0] += 1
	if t == 'n':
		index[0] += 1
		return None
	if t in 'ilfsb':
		x = read_till_bang(string, index)
		if t == 'i': return int(x)
		if t == 'l':
			if sys.version > '3':
				return int(x)
			return long(x)
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
	return _send_command('authenticate', { 'user': username, 'password': password })

def send_poll(user_id, password, sector_you_care_about, last_ids_by_sector):
	sectors = _get_poll_args(sector_you_care_about, last_ids_by_sector)
	return _send_command('poll', { 'sectors': sectors }, user_id, password)

def _get_poll_args(sector, last_ids_by_sector):
	nsectors = {}
	if '^' in str(sector):
		x,y = util.totuple(sector)
	else:
		x,y = sector
	
	for dx in (-1, 0, 1):
		for dy in (-1, 0, 1):
			nsectors[(x + dx, y + dy)] = True
	s_r = []
	for s in nsectors.keys():
		last_id = last_ids_by_sector.get(s, 0)
		s_r.append(str(last_id) + '^' + util.fromtuple(s))
	return ','.join(s_r)

def send_username_fetch(user_ids):
	return _send_command('getuser', { 'user_id_list': ','.join(map(str, user_ids)) })

def send_build(user_id, password, type, sector_x, sector_y, loc_x, loc_y, sector_you_care_about, last_ids_by_sector, client_token):
	poll_sectors = _get_poll_args(sector_you_care_about, last_ids_by_sector)
	return _send_command('build', {
		'type': type,
		'sector': util.fromtuple((sector_x, sector_y)),
		'loc': util.fromtuple((loc_x, loc_y)),
		'client_token': client_token,
		'poll_sectors': poll_sectors
		}, user_id, password)
	
def send_demolish(user_id, password, sector_x, sector_y, x, y, client_token):
	return _send_command('demolish', {
		'sector': util.fromtuple((sector_x, sector_y)),
		'loc': util.fromtuple((x, y)),
		'client_token': client_token
	}, user_id, password)