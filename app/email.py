from flask import render_template
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

def sendPasswordResetEmail(user):
    token = user.get_reset_password_token()
    sendEmail('[PUPQC-ESIS] Reset Your Password',
                recipients=[user.Email],
                text_body=render_template('email/reset_password.txt', user=user, token=token),
                html_body=render_template('email/reset_password.html', user=user, token=token))
