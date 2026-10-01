import requests
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_email_alert(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = os.getenv("SMTP_USER")
    msg["To"] = to_email
    try:
        with smtplib.SMTP(os.getenv("SMTP_HOST"),int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"),os.getenv("SMTP_PASS"))
            server.send_message(msg)
        print(f"Alert sent to {to_email}")
    except Exception as e:
        print(f"Failed to sent to {to_email}: {e}")
        
    
