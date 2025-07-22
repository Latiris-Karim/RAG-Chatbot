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

class Emails:
    def __init__(self, smtp_server: str = 'smtp.gmail.com', smtp_port: int = 465):
        
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = os.getenv('MY_EMAIL')
        self.sender_password = os.getenv('MY_EMAIL_PASSWORD')
   
        if not self.sender_email or not self.sender_password:
            raise ValueError("Email credentials not found in environment variables")
        
    def send_verification_email(self, user_email, code):
         
         msg = EmailMessage()
         msg['Subject'] = 'Your Verification Code'
         msg['From'] = self.sender_email
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
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
                  smtp.login(self.sender_email, self.sender_password)
                  smtp.send_message(msg)
            print("Verification email sent successfully.")
         except Exception as e:
            print(f"Error sending email: {e}")

    def subscription_success(self, user_email):
      """Send first subscription payment success email."""
      if not user_email:
         print("Error: Email is required")
         return False
      
      msg = EmailMessage()
      msg['Subject'] = 'Welcome! Your Subscription is Active'
      msg['From'] = self.sender_email
      msg['To'] = user_email
      
      content = f"""Hello!

         Thank you for subscribing!

         Your first payment has been processed successfully, and your subscription is now active.

         What's next?
         • You now have full access to all premium features
         • Your subscription will automatically renew monthly
         • You can manage your subscription anytime in your account settings

         If you have any questions, feel free to reach out to our support team.

         Welcome aboard!

         Best regards,
         Your Team"""
      
      msg.set_content(content)
      
      try:
         with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
               smtp.login(self.sender_email, self.sender_password)
               smtp.send_message(msg)
         print(f"Subscription success email sent to {user_email}")
         return True
      except Exception as e:
         print(f"Error sending subscription success email: {e}")
         return False
      
    def subscription_renewal(self, user_email):
      """Send subscription renewal confirmation email."""
      if not user_email:
         print("Error: Email is required")
         return False
   
      
      msg = EmailMessage()
      msg['Subject'] = 'Payment Confirmed - Subscription Renewed'
      msg['From'] = self.sender_email
      msg['To'] = user_email
      
      content = f"""Hello!

            Your subscription has been successfully renewed.


            Your subscription remains active and you continue to have full access to all premium features.
            Thank you for your continued subscription!

            Best regards,
            Your Team"""
      
      msg.set_content(content)
      
      try:
         with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
               smtp.login(self.sender_email, self.sender_password)
               smtp.send_message(msg)
         print(f"Subscription renewal email sent successfully to {user_email}")
         return True
      except Exception as e:
         print(f"Error sending renewal email: {e}")
         return False
      


    def subscription_cancelled(self, user_email, expire_date):
      """Send subscription cancellation confirmation email."""
      if not user_email:
         print("Error: Email is required")
         return False

      msg = EmailMessage()
      msg['Subject'] = 'Subscription Cancelled - Confirmation'
      msg['From'] = self.sender_email
      msg['To'] = user_email
      
      content = f"""Hello!

         Your subscription has been successfully cancelled as requested.

         Your access to premium features will continue until the end of your current billing period: {expire_date}. After that, your account will be downgraded to our free tier.

         We're sorry to see you go! If you change your mind, you can reactivate your subscription at any time through your account settings.

         If you cancelled due to an issue, please let us know how we can improve - your feedback is valuable to us.

         Best regards,
         Your Team"""
      
      msg.set_content(content)
      
      try:
         with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
               smtp.login(self.sender_email, self.sender_password)
               smtp.send_message(msg)
         print(f"Subscription cancellation email sent successfully to {user_email}")
         return True
      except Exception as e:
         print(f"Error sending cancellation email: {e}")
         return False
      


    def subscription_failed(self, user_email: str):
      """Send subscription renewal failure email."""
      if not user_email:
         print("Error: Email is required")
         return False

      msg = EmailMessage()
      msg['Subject'] = 'Payment Failed - Subscription Renewal Issue'
      msg['From'] = self.sender_email
      msg['To'] = user_email
      
      content = f"""Hello!

         We were unable to process your subscription renewal payment.

         Your subscription will expire soon if payment is not completed. To avoid any interruption to your service, please update your payment information or retry your payment.

         You can update your payment details by logging into your account or contacting our support team.

         If you have any questions or need assistance, please don't hesitate to reach out to us.

         Best regards,
         Your Team"""
      
      msg.set_content(content)
      
      try:
         with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
               smtp.login(self.sender_email, self.sender_password)
               smtp.send_message(msg)
         print(f"Subscription failure email sent successfully to {user_email}")
         return True
      except Exception as e:
         print(f"Error sending failure email: {e}")
         return False
      
    def pw_reset_email(self, user_email, url):
      if not user_email:
            print("Error: Email is required")
            return False

      msg = EmailMessage()
      msg['Subject'] = 'Password Reset Request'
      msg['From'] = self.sender_email
      msg['To'] = user_email

      content = f"""Hello!

            We received a request to reset your password for your account.

            To reset your password, please click the link below:
            {url}

            This link will expire in 30 minutes for security reasons.

            If you did not request a password reset, please ignore this email. Your password will remain unchanged.

            For security reasons, please do not share this link with anyone.

            If you have any questions or need assistance, please don't hesitate to reach out to us.

            Best regards,
            Your Team"""
      
      msg.set_content(content)
      
      try:
         with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
               smtp.login(self.sender_email, self.sender_password)
               smtp.send_message(msg)
         print(f"Password reset email sent successfully to {user_email}")
         return True
      except Exception as e:
         print(f"Error sending password reset email: {e}")
         return False

    def email_change_verification(self, user_email, verification_code):
            if not user_email:
               print("Error: Email is required")
               return False

            msg = EmailMessage()
            msg['Subject'] = 'Email Change Verification'
            msg['From'] = self.sender_email
            msg['To'] = user_email

            content = f"""Hello!

         We received a request to change your email address for your account.

         To complete the email change, please enter the verification code below:

         {verification_code}

         This code will expire in 15 minutes for security reasons.

         If you did not request an email change, please ignore this email and contact us immediately as someone may be trying to access your account.

         For security reasons, please do not share this code with anyone.

         If you have any questions or need assistance, please don't hesitate to reach out to us.

         Best regards,
         Your Team"""
            
            msg.set_content(content)
            
            try:
               with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
                  smtp.login(self.sender_email, self.sender_password)
                  smtp.send_message(msg)
               print(f"Email change verification code sent successfully to {user_email}")
               return True
            except Exception as e:
               print(f"Error sending email change verification: {e}")
               return False
