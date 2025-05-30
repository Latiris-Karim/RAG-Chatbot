import smtplib
from email.message import EmailMessage
import os 
import sys


if __name__ == "__main__":  #to test without api calls 
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.database import Database
from src.db.email_db import get_verification_code


db = Database()

def verify_emailcode(submitted_code, email):

   select_query = "SELECT id FROM users WHERE email = %s"
   result = db.fetch_query(select_query, (email,))
   u_id = result[0]['id']
   stored_code = get_verification_code(u_id)
   
   if submitted_code == stored_code:
      update_query = '''UPDATE users SET verified = TRUE WHERE id = %s'''
      db.execute_query(update_query, (u_id,))
      return {'message':'Email successfully verified'}
   else:
      return {'message':'Invalid verification code'}

def send_email(user_email, code):
   
   myemail = os.getenv('MY_EMAIL')

   msg = EmailMessage()
   msg['Subject'] = 'Your Verification Code'
   msg['From'] = myemail
   msg['To'] = user_email
   

   msg.set_content(f'''
    Hello!

    Thank you for registering.

    Your verification code is: {code}

    Please enter this code to verify your account.

    Regards,
    Your Team
    ''')

   try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(myemail, os.getenv('MY_EMAIL_PASSWORD'))
            smtp.send_message(msg)
        print("Verification email sent successfully.")
   except Exception as e:
        print(f"Error sending email: {e}")


