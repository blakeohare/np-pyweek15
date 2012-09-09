import sql
import util

# ideally add a separate module for each command

def do_things(action, args):
	
	output = { 'success': False, 'message': "Unrecognized command" }
	
	if action == 'register':
		user = args.get('user', '')
		password = args.get('password', '')
		# TODO: register
	elif action == 'poll':
		pass
	elif action == 'echo':
		output = { 'success': True, 'data': args.get('data', None) }
	# et cetera
	
	return output
