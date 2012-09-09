import sql
import util

# ideally add a separate module for each command

def do_things(action, args):
	
	output = { 'success': False, 'message': "Unrecognized command" }
	
	if action == 'register':
		user = args.get('user', '')
		password = args.get('password', '')
		if(sql.query('select user_id from user where name=%s',(user,) )
			output={'success':False}
		else:
			user_id=add_user(user, password)
			if user_id:
				output = {'success':True}
			else:
				output = {'success':False}
		
	elif action == 'poll':
		output='success':True,'sectors':build_sector_response(args)}
	elif action == 'echo':
		output = { 'success': True, 'data': args.get('data', None) }
	elif action == 'build':
		if authenticate(args):
			token=args.get('client_token')
			success=False;
			if token:
				duplicate=sql.query('select author_token from event where author_token=%s',token)
				if not duplicate:
					#add it to the table, I guess?
					sector='0^0'
					type=args.get('type')
					if sector is None:
						sector = 'NULL'
					data='No data yet'
					sql.insert('insert into event (author_token, sector_xy,type,data) values (%s,%s,%s,%s)',(token, sector,type,data)
					success=True
			output={'success':success,'sectors':build_sector_response(args)}
			
		else:
			output = {'success':False}
	# et cetera
	
	return output


def build_poll_update(args, output):
	sectorIds=args.get('sectors','').split(',')
	minId=None
	inValues=[]
	minimums={}
	for sectorId in sectorIds:
		id,xy=sectorId.split('^',1)
		id=int(id)
		inValues.append(xy)
		minvalues[xy]=id
		if minId is None or id<minId:
			minId=id
	if minId is None:
		minId=0
	#yes this opens up sql injection, but only here, and only on sector_xy parts
	query='select * from event where event_id>%i and sector_xy in (%s) or sector_xy is null'%(minId, ','.join(sectors))
	events=sql.query(query)
	responses={}
	maxId=minId
	for row in events:
		sector=row['sector_xy']
		maxId=max(maxId,row['event_id'])
		#todo remove client_token
		if(sector is None):
			add_to_dictlist(responses,'global',{'data':row['data'],'client_token':client_token, 'event_id':event_id})
		else
			minval=minimums[sector]
			if row['event_id']>minval:
				add_to_dictlist(responses,sector,{'data':row['data'],'client_token':client_token, 'event_id':event_id}
	output['sectors']=responses
	
def add_to_dictlist(dictlist,key,value):
	if key in dictlist:
		items=dictlist[key]
		items.append(value)
	else:
		dictlist[key]=[value]
			
#checks args instead of value because we'll use for lots of things
def authenticate(args):
	user=args.get('user')
	password=args.get('password')
	if user and password:
		if sql.query('select * from user where name=%s and value=%s', (user,args)):
			return True
	return False

def add_user(user, password):
	sector='0^0'
	location='0^0'
	crystals=0
	user_id=sql.insert('INSERT into user (name, password, hq_sector,hq_xy,crystals) values (%s,%s,%s,%s,%i)',(user,password,sector,location,crystals) )
