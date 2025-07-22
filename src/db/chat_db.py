import sys
import os
import random

if __name__ == "__main__":  #to test without api calls 
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.database import Database
from src.utils.constants import LOL_Room_Names

db = Database()


def create_chatroom(u_id): 
    room = random.choice(LOL_Room_Names)


    insert_query = """INSERT INTO chat_rooms (user_id, title) VALUES (%s, %s)"""
    db.execute_query(insert_query, (u_id, room))
    
    select_query = """SELECT id FROM chat_rooms WHERE user_id = %s ORDER BY created_at DESC LIMIT 1"""
    res = db.fetch_query(select_query, (u_id,))
    chatroom_id = res[0]['id']
    
    return {
        "message": "Chatroom created",
        "chatroom_id": chatroom_id,
        "title": room
    }  
    
    
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

def clean_text(text):
    unwanted_patterns = ["\n\n2.", "\n—", "\n2."]
    for pattern in unwanted_patterns:
        text = text.replace(pattern, "")
    return text.strip()

def recent_chathistory(chatroom_id):
    select_query = '''SELECT role, msg FROM messages WHERE chat_room_id = %s ORDER BY created_at DESC LIMIT 10'''
    results = db.fetch_query(select_query, (chatroom_id,))

    formatted_messages = []
    for row in results:
        role = clean_text(row['role']).capitalize()
        message = clean_text(row['msg'])
        formatted_messages.append(f"{role}: {message}")

    chathistory = "\n".join(reversed(formatted_messages))
    return chathistory
