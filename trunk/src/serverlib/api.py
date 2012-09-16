from serverlib import sql

def get_user_info():
	return sql.query("SELECT `user_id` AS 'id',`name`, `research` AS 'bytes', `hq_sector`, `hq_loc` FROM `user`")
	
	