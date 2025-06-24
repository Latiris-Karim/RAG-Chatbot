from src.config.database import Database

db = Database()

def increase_query_counter(u_id):
    insert_query = '''INSERT INTO user_activity (user_id) VALUES (%s)'''
    db.execute_query(insert_query, (u_id,))

def get_user_query_count(u_id):
    select_query = '''SELECT count(*) FROM user_activity WHERE user_id = %s AND created_at::date = CURRENT_DATE'''
    res = db.fetch_query(select_query,(u_id,))
    return res[0]['count']

def is_user_at_limit(u_id):
    return get_user_query_count(u_id) >= 3

def get_time_until_reset():
    select_query = '''SELECT EXTRACT(EPOCH FROM (DATE_TRUNC('day', NOW()) + INTERVAL '1 day' - NOW())) as seconds_until_midnight'''
    res = db.fetch_query(select_query)
    seconds_left = res[0]['seconds_until_midnight']
    hours_left = seconds_left / 3600
    return hours_left
