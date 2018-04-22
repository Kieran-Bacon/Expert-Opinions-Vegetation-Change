from ExpertWebtool import TEMPLATES

import os, smtplib
from email.message import EmailMessage

def email(subject: str, to: str, template: str, formatting: [str]):

    # Create email information
    email = EmailMessage()
    email["Subject"] = subject
    email["To"] = to
    email["From"] = "ExpertClimateWebtool@gmail.com"

    # Set e-mail contents
    with open(os.path.join(TEMPLATES, template)) as filehandler:
        email.set_content(filehandler.read().format(*formatting))

    # Send the message via our own SMTP server.
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)  
    s.starttls()
    s.login("ExpertClimateWebtool@gmail.com", "Exeter1!")
    s.send_message(email)
    s.quit()