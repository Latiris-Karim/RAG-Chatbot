from src.config.database import Database
from src.db.user_db import get_email
from src.db.subscription_db import get_sub_status
from src.services.email_service import Emails
from src.db.subscription_db import cancel_stripe_subscription, get_sub_id
import bcrypt
import datetime
from datetime import timedelta
import secrets
from email_validator import validate_email, EmailNotValidError

db = Database

def change_pw(u_id, new_password):
    if not new_password or len(new_password) == 0:
            return {"message":"Password cannot be empty"}
    if len(new_password) < 6:
            return {"message":"Password must be atleast 6 characters long"}
       
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    hashed_password_string = hashed_password.decode('utf-8')
    update_query = '''UPDATE users SET password_hash = %s WHERE u_id = %s'''

    db.execute_query(update_query, (hashed_password_string,u_id))
    return {'message':'Password has been changed'}

def forgot_pw(email):#cant access account
    select_query = '''SELECT email FROM users WHERE email = %s'''
    res = db.fetch_query(select_query,(email,))
    if not res[0]['email']:
         return {"message": "If the email exists, a reset link has been sent"}
    
    reset_token = secrets.token_urlsafe(32)
    expiry = datetime.now() + timedelta(minutes=30)
    store_reset_token(email, reset_token, expiry)

    reset_url = f"https://mysite.com/reset-password?token={reset_token}"
    Emails.pw_reset_email(email, reset_url)
    
    return {"message": "Reset email sent"}
    
def reset_password(token, new_password):
    select_query = '''SELECT id FROM users WHERE reset_token = %s AND reset_token_expiry > NOW()'''
    res = db.fetch_query(select_query, (token,))
    
    u_id = res[0]['id']
    if not u_id:
        return {"message": "Invalid or expired reset token"}
    res = change_pw(u_id, new_password)
    return res
    
def user_info(u_id):
    email = get_email(u_id)
    sub_status = get_sub_status(u_id)
    return {'email': email, 'sub_status':sub_status}

def store_reset_token(email, reset_token, expiry):
    update_query = '''UPDATE users SET reset_token = %s, reset_token_expiry = %s WHERE email = %s'''
    db.execute_query(update_query, (reset_token, expiry, email))

def change_email_request(u_id, new_email):
   if not new_email:
       return {'message': 'Please enter a valid email'}
   
   try:
       validated_email = validate_email(new_email)
       normalized_email = validated_email.email

   except EmailNotValidError:
       return {'message': 'Please enter a valid email address'}
   
   email_code = secrets.token_urlsafe(32)
   update_query = '''UPDATE users SET new_email = %s, new_email_code = %s WHERE id = %s'''
   db.execute_query(update_query, (normalized_email, email_code, u_id))
   Emails.email_change_verification(normalized_email, email_code)
   return {'message': 'Email change request has been submitted, check your new email'}

def activate_new_email(u_id, new_email):
     new_email = get_new_email(u_id)
     update_query = '''UPDATE users SET email = %s WHERE id = %s'''
     db.execute_query(update_query, (new_email, u_id))

def get_new_email(u_id):
     select_query = '''SELECT new_email FROM users WHERE id = %s'''
     res = db.fetch_query(select_query, (u_id,))
     new_email = res[0]['new_email']
     if new_email:
        return new_email
     return {'message':'No new email was specified'}

def get_email_code(u_id):
     select_query = '''SELECT new_email_code FROM users WHERE id = %s'''
     res = db.fetch_query(select_query, (u_id,))
     new_email = res[0]['new_email_code']
     if new_email:
        return new_email
     return {'message':'No new email was specified'}

def change_email(u_id, userinput):
    dbcode = get_email_code(u_id)
    if dbcode == userinput:
        new_email = get_new_email(u_id)
        activate_new_email(u_id, new_email)
        return {'message':'Your email was succesfully update'}
    
    return {'message':'Wrong code or empty code submitted'}
    
def delete_account(u_id):
    sub_id = get_sub_id(u_id) 
    if sub_id:
        cancel_stripe_subscription(sub_id)
        
    delete_query = '''DELETE FROM users WHERE id = %s'''
    db.execute_query(delete_query, (u_id,))
    return {"message":"Account deleted successfully!"}
    

