import os
from email.message import EmailMessage
import ssl
import smtplib

email_sender = 'maxim.polochkin1@gmail.com'
email_password = 'styj gbgk pyyo yrns'


def send_reg_code(register_code, email_receiver):
    subject = 'Register Code: %s' % register_code
    body = 'Register Code: %s\nCheck out my website: https://pyproject-assistant.netlify.app/' % register_code

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
