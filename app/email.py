from flask_mail import Message
from app import mail, app
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
    Thread(target=sendAsyncEmail, args=(app, msg)).start()