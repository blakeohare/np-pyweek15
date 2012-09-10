import sql
import util
from serverlib import authenticate
from serverlib import poll

# ideally add a separate module for each command

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
				
				return poll.do_poll(args.get('sectors'))
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
			else:
				return { 'success': False, 'message': "Unrecognized command" }
		else:
			return { 'success': False, 'message': "Invalid username/password." }	
