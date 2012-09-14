import sql
import util
from serverlib import authenticate
from serverlib import poll

# If for some reason, the server needs to move,
# this server should return a { 'redirect': "http://newserver.com" }
# The address should be everything up to (but not including) the /server.py?...


def do_things(action, args):
	
	if action == 'echo':
		return { 'success': True, 'data': args.get('data', None) }
	elif action == 'authenticate':
		return authenticate.heavy_authenticate(args.get('user', ''), args.get('password', ''), True)
	elif action == 'getuser':
		from serverlib import getuser
		return getuser.get_user(args.get('user_id_list', None))
		
	else:
		user_id = util.parseInt(args.get('user_id', 0))
		
		if authenticate.light_authenticate(user_id, args.get('password', '')):
			if action == 'poll':
				
				return poll.do_poll(user_id, args.get('sectors'))
			elif action == 'build':
				from serverlib import build
				return build.do_build(
					user_id,
					args.get('client_token'),
					args.get('last_id'),
					args.get('sector'),
					args.get('loc'),
					args.get('type'))
				
			elif action == 'demolish':
				from serverlib import demolish
				return demolish.do_demolish(
					user_id,
					args.get('last_id'),
					args.get('sector'),
					args.get('loc'),
					args.get('client_token'))
			elif action == 'radar':
				from serverlib import neighbors
				return neighbors.find_neighbors(
					user_id,
					args.get('rx', None),
					args.get('ry', None))
			elif action == 'research':
				from serverlib import research
				return research.apply_research(
					user_id,
					args.get('type', None))
			else:
				return { 'success': False, 'message': "Unrecognized command" }
		else:
			return { 'success': False, 'message': "Invalid username/password." }	
