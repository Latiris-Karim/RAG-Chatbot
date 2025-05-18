import sys
import os


if __name__ == "__main__":  #to test without api calls 
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.database import Database
import bcrypt
from src.utils.jwt_handler import create_token


db = Database()

def register(email, pw):
    if email_exists(email) == False:

        hashed_password = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
        hashed_password_string = hashed_password.decode('utf-8')
    
        insert_query = """INSERT INTO users (email, password_hash) VALUES (%s, %s) """
        db.execute_query(insert_query, (email,hashed_password_string))
        return {"message":"Account successfully registered"}
    else:
        return {"message":"Email is taken"}


def email_exists(email):
    select_query = "SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)"
    result = db.fetch_query(select_query, (email,))
    return result[0]['exists'] if result else False

def login(email: str, pw: str):
    select_query = """SELECT id, password_hash FROM users WHERE email = %s"""
    result = db.fetch_query(select_query, (email,))
    
    if not result:
        return {"message": "Invalid email or password"}
    
    user_id = result[0]['id']
    stored_hash = result[0]['password_hash']
    
    if bcrypt.checkpw(pw.encode('utf-8'), stored_hash.encode('utf-8')):
        token = create_token(user_id)
        
        return {
            "message": "Login successful", 
            "user_id": user_id,
            "token": token
        }
    else:
        return {"message": "Invalid email or password"}
    

