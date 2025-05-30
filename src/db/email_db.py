from src.config.database import Database 

db = Database()


def get_verification_code(u_id):
    try:
        select_query = '''SELECT code FROM users WHERE id = %s'''
        result = db.fetch_query(select_query, (u_id,))
    
        if result and len(result) > 0:
            return result[0]['code']
        else:
            print(f"No verification code found for user {u_id}")
            return None
    except Exception as e:
        print(f"Error getting verification code: {e}")
        return None
