	import MySQLdb

_connection = None
_credentials = None

def connect(host, user, password, db):
	global _connection, _credentials
	_credentials = (host, user, password, db)

def query(query, args=None):
	global _connection, _credentials
	if _connection == None:
		cred = _credentials
		_connection = MySQLdb.connect(host = cred[0], user = cred[1], passwd = cred[2], db = cred[3])
	cursor = _connection.cursor()
	if args:
		cursor.execute(query, args)
	else:
		cursor.execute(query)
	result = cursor.fetchall()
	columns = cursor.description
	cursor.close()
	output = []
	for row in result:
		lookup = {}
		i = 0
		while i < len(columns):
			lookup[columns[i][0]] = row[i]
			i += 1
		output.append(lookup)
	return output

def insert(query, args=None):
	global _connection, _credentials
	if _connection == None:
		cred = _credentials
		_connection = MySQLdb.connect(host = cred[0], user = cred[1], passwd = cred[2], db = cred[3])
	cursor = _connection.cursor()
	if args:
		cursor.execute(query, args)
	else:
		cursor.execute(query)
	cursor.close()
	return cursor.lastrowid

def cleanup():
	global _connection
	if _connection != None:
		_connection.close()
		_connection = None
		