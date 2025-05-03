# modules/email_utils.py

import smtplib
from email.message import EmailMessage
import os

def send_email_receipt(gmail_user, gmail_app_password, to_email, subject, body_text, pdf_path):
    """
    Send an email with a PDF attachment using Gmail.
    
    Parameters:
        gmail_user (str): Your Gmail address
        gmail_app_password (str): Your Gmail app password
        to_email (str): Recipient email
        subject (str): Subject of the email
        body_text (str): Body text
        pdf_path (str): Path to PDF file to attach
    """
    try:
        msg = EmailMessage()
        msg["From"] = gmail_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body_text)

        with open(pdf_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(pdf_path)

        msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_user, gmail_app_password)
            smtp.send_message(msg)

        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Failed to send email: {e}"
