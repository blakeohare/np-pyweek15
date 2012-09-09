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
		return self.response
	
	def is_error(self):
		return self.error
	
	def send(self):
		self.start()

def _send_command(action, args, user=None, password=None):
	request = Request(action, args, user, password)
	request.send()
	return request

def send_echo(stuff):
	return _send_command("echo", { 'data': stuff })