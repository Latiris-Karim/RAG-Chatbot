import sys
import os


if __name__ == "__main__":  #to test without api calls 
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.database import Database

db = Database()

def create_chatroom(chatroom_id, u_id):#add title somehow... 
    try:
        check_query = '''SELECT id FROM chat_rooms WHERE chatroom_id = %s and user_id = %s'''
        existing = db.fetch_query(check_query,(chatroom_id, u_id))
        roomtitle = "Room" + str(chatroom_id)
        if existing:
            return{"message":"Chatroom ID in use"}
        
        insert_query = """INSERT INTO chat_rooms (chatroom_id, user_id, title) VALUES (%s, %s, %s) """
        db.execute_query(insert_query, (chatroom_id, u_id, roomtitle))
        return {"message":"Chatroom created"}
    
    except Exception as e:
        print(f"Error creating chatroom: {str(e)}")
        return {"status": "error", "message": "Failed to create chatroom"}
    
def save_msg(msg, chatroom_id, u_id, role='user'):
    if not msg or not chatroom_id or not u_id:
        print("Error: Missing required parameters")
        return False
       
    if role not in ['user', 'ai']:
        raise ValueError("Role must be either 'user' or 'ai'")
   
    try:
        insert_query = '''INSERT INTO messages (msg, chat_room_id, sender_id, role)
                          VALUES (%s, %s, %s, %s)'''
        result = db.execute_query(insert_query, (msg, chatroom_id, u_id, role))
       
        return {
        'message': f'Message from {role} saved successfully!',
        'query': result
    }
    except Exception as e:
        print(f"Error saving message: {e}")
        return False
    
def get_chatrooms(u_id):#save id for each chatroom to use as fk for getting respective messages
    try:
        select_query = '''SELECT id, title FROM chat_rooms WHERE user_id = %s'''
        result = db.fetch_query(select_query,(u_id,))
        return {'message':'user chatrooms:'},  result
    
    except Exception as e:
        print("Error", e)

def get_chatroom_msgs(chatroom_id, u_id):
    try:
        select_query = '''SELECT msg,role FROM messages WHERE chat_room_id = %s and sender_id = %s'''
        result = db.fetch_query(select_query, (chatroom_id, u_id))
        return result
    except Exception as e:
        print("Error", e)

