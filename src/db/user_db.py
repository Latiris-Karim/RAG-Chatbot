import sys
import os
import random
import string
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timedelta

if __name__ == "__main__":  #to test without api calls 
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.database import Database
import bcrypt
from src.services.email_service import Emails

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
        emails = Emails()
        emails.send_verification_email(email, code)
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
        from src.utils.jwt_handler import create_token_pair
        tokens = create_token_pair(user_id)
        
        return {
            "message": "Login successful", 
            "user_id": user_id,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"]
        }
    else:
        if user_verified == False:
            return {"message": "Please verify your email"}
        
        return {"message": "Wrong email or password"}
    
def get_email(u_id):
    select_query = """SELECT email FROM users WHERE id = %s"""
    result = db.fetch_query(select_query, (u_id,))
    return result[0]['email']
    

def store_customer_id(u_id, customer_id):
    update_query = '''UPDATE users SET customer_id = %s WHERE id = %s'''
    db.execute_query(update_query, (customer_id, u_id))
    return True
     

def get_customer_id(u_id):
    select_query = '''SELECT customer_id FROM users WHERE id=%s'''
    result = db.fetch_query(select_query, (u_id,))
        
    if result[0]['customer_id']:
        return result[0]['customer_id'] 
    return None

   
def store_refresh_token(u_id, token_hash):
    delete_query = 'DELETE FROM refresh_tokens WHERE user_id = %s'
    db.execute_query(delete_query, (u_id,))
    
    insert_query = '''
        INSERT INTO refresh_tokens (token_hash, user_id, expires_at, created_at)
        VALUES (%s, %s, %s, %s)
    '''
    db.execute_query(insert_query, (token_hash, u_id, datetime.utcnow() + timedelta(days=7), datetime.utcnow()))


def get_stored_refresh_token(u_id):
    select_query = '''SELECT token_hash FROM refresh_tokens WHERE user_id = %s'''
    result = db.fetch_query(select_query, (u_id,))
    return result[0]['token_hash']

def delete_refresh_token(user_id: int):
    """Delete refresh token on logout"""
    delete_query = 'DELETE FROM refresh_tokens WHERE user_id = %s'
    db.execute_query(delete_query, (user_id,))

def get_user_by_refresh_token(hash_token):
    select_query = '''SELECT user_id FROM refresh_tokens WHERE token_hash = %s'''
    result = db.fetch_query(select_query,(hash_token,))
    return result[0]['user_id']
