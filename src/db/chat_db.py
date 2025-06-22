import sys
import os
import random

if __name__ == "__main__":  #to test without api calls 
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.database import Database
from src.utils.constants import LOL_Room_Names

db = Database()


def create_chatroom(u_id, max_retries=3): 
     for attempt in range(max_retries):
        try:
            chatroom_id = random.randint(1, 10000)
            room = random.choice(LOL_Room_Names)
            
            
            insert_query = """INSERT INTO chat_rooms (chatroom_id, user_id, title) VALUES (%s, %s, %s)"""
            db.execute_query(insert_query, (chatroom_id, u_id, room))
            
            return {
                "message": "Chatroom created",
                "chatroom_id": chatroom_id,
                "title": room
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            if ("duplicate" in error_msg or "unique" in error_msg) and attempt < max_retries - 1:
                continue  
            else:
                print(f"Error creating chatroom: {str(e)}")
                return {"status": "error", "message": "Failed to create chatroom"}
    
    
def save_msg(msg, chatroom_id, u_id, role='user'):
    if not msg or not chatroom_id or not u_id:
        print("Error: Missing required parameters")
        return False
       
    if role not in ['user', 'ai']:
        raise ValueError("Role must be either 'user' or 'ai'")
   
    insert_query = '''INSERT INTO messages (msg, chat_room_id, sender_id, role)
                          VALUES (%s, %s, %s, %s)'''
    result = db.execute_query(insert_query, (msg, chatroom_id, u_id, role))
       
    return {
        'message': f'Message from {role} saved successfully!',
        'query': result
    }
    

def get_chatrooms(u_id):
    select_query = '''SELECT id, title FROM chat_rooms WHERE user_id = %s'''
    result = db.fetch_query(select_query,(u_id,))
    return {'message':'user chatrooms:'},  result


def get_chatroom_msgs(chatroom_id):
    select_query = '''SELECT msg,role FROM messages WHERE chat_room_id = %s'''
    result = db.fetch_query(select_query, (chatroom_id,))
    return result
    

def access_to_chatroom(chatroom_id, u_id):
    select_query = '''SELECT COUNT(*) FROM chat_rooms WHERE id = %s and user_id = %s'''
    result = db.fetch_query(select_query,(chatroom_id, u_id))
    return result[0]['count'] > 0
    
   
