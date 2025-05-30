import sys
import os
import random
import string
from email_validator import validate_email, EmailNotValidError

if __name__ == "__main__":  #to test without api calls 
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.database import Database
import bcrypt
from src.utils.jwt_handler import create_token
from src.services.email_service import send_email

db = Database()

def register(email, pw):
    if email_exists(email) == False:

        if not pw or len(pw) == 0:
            return {"message":"Password cannot be empty"}
        if len(pw) < 6:
            return {"message":"Password must be atleast 6 characters long"}
        try:
            emailvalid = validate_email(email, check_deliverability=True)
            email = emailvalid.normalized

        except EmailNotValidError as e:
            print(str(e))
            return {"message":"Invalid email address"}

        hashed_password = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
        hashed_password_string = hashed_password.decode('utf-8')
        code = ''.join(random.choices(string.digits, k=4))
        insert_query = """INSERT INTO users (email, password_hash, code) VALUES (%s, %s, %s) """
        db.execute_query(insert_query, (email,hashed_password_string,code))
        send_email(email, code)
        return {"message":"Account successfully registered"}
    else:
        return {"message":"Email is taken"}

def get_userid(email):
    select_query = "SELECT id FROM users WHERE email = %s"
    result = db.fetch_query(select_query, (email,))
    return result[0]['id']

def email_exists(email):
    select_query = "SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)"
    result = db.fetch_query(select_query, (email,))
    return result[0]['exists'] if result else False

def user_status(u_id):
    select_query = "SELECT verified FROM users WHERE id = %s"
    result = db.fetch_query(select_query, (u_id,))
    return result[0]['verified']

def login(email: str, pw: str):
    select_query = """SELECT id, password_hash FROM users WHERE email = %s"""
    result = db.fetch_query(select_query, (email,))
    
    if not result:
        return {"message": "Invalid email or password"}
    
    user_id = result[0]['id']
    stored_hash = result[0]['password_hash']
    user_verified = user_status(user_id)

    if bcrypt.checkpw(pw.encode('utf-8'), stored_hash.encode('utf-8')) and user_verified == True:
        token = create_token(user_id)
        
        return {
            "message": "Login successful", 
            "user_id": user_id,
            "token": token
        }
    else:
        if user_verified == False:
            return {"message": "Please verify your email"}
        
        return {"message": "Wrong email or password"}
    
def get_email(u_id):
    select_query = """SELECT email FROM users WHERE id = %s"""
    result = db.fetch_query(select_query, (u_id,))
    return result[0]['email']


