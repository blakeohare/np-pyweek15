#!/usr/local/bin/python

print "Content-type: text/html\n"

try:
	import protected
	import traceback
	import cgi
	from serverlib import util
	from serverlib import sql
	from serverlib import executor
	
	# GET parameters
	rawArgs = cgi.FieldStorage()
	args = {}
	for key in rawArgs.keys():
		args[key] = rawArgs[key].value
	
	# Connect to SQL database. 
	stuff = protected.get_credentials()
	
	action = args.get('action', '')
	output = executor.do_things(action, args)
	
	# when completed, format_output can take any recursive non-cyclic data 
	# structure containing any of the following:
	# - dictionaries with string keys
	# - lists
	# - strings
	# - ints
	# - bools
	# - floats
	# - None
	# Longs or class instances will NOT be supported. Tuples will be accepted but
	# will manifest themselves as normal lists on the other side of the worm hole. 
	# Right now this just wraps a call to str(). I'll ping you before I make the
	# changes or include an option to use a &debug=1 flag in the URL to fall back
	# to str() behavior.
	print util.format_output(output)
	
	sql.cleanup()
	
except:
	print traceback.format_exc().replace('<', '&lt;').replace('\n', '<br />')