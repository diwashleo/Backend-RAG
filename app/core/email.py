import os
import smtplib
from email.message import EmailMessage
from typing import Optional

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "no-reply@diwash.com")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

class EmailSendError(Exception):
    pass

def send_booking_email(to_email: str, subject: str, body_text: str, body_html: Optional[str] = None):
    if not SMTP_HOST:
        raise EmailSendError("SMTP_HOST not configured")
    
    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body_text)
    if body_html:
        msg.add_alternative(body_html, subtype="html")
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            if SMTP_USE_TLS:
                server.starttls()
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        raise EmailSendError(f"Failed to send email: {e}")