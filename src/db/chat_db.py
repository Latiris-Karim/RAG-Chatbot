import sys
import os


if __name__ == "__main__":  #to test without api calls 
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.database import Database

db = Database()

def create_chatroom(u_id, chatroom_id):
    try:
        check_query = '''SELECT id FROM chat_rooms WHERE id = %s'''
        existing = db.fetch_query(check_query,(chatroom_id,))

        if existing:
            return{"message":"Chatroom ID in use"}
        
        insert_query = """INSERT INTO chat_rooms (id, created_by) VALUES (%s, %s) """
        db.execute_query(insert_query, (chatroom_id, u_id))
        return {"message":"Chatroom created"}
    
    except Exception as e:
        print(f"Error creating chatroom: {str(e)}")
        return {"status": "error", "message": "Failed to create chatroom"}

    
    
print(create_chatroom(3,1))
