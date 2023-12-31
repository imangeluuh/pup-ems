from flask import render_template, current_app
from flask_mail import Message
from app import mail
from threading import Thread

# Function to send an email asynchronously
def sendAsyncEmail(app, msg):
    with app.app_context():
        mail.send(msg)

# Function to send an email asynchronously with threading
def sendEmail(subject, recipients, text_body, html_body):
    msg=Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # Create a new Thread to send the email asynchronously
    Thread(target=sendAsyncEmail, args=(current_app._get_current_object(), msg)).start()
