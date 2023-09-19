from flask_mail import Message
from app import mail, app
from threading import Thread

def sendAsyncEmail(app, msg):
    with app.app_context():
        mail.send(msg)


def sendEmail(subject, recipients, text_body, html_body):
    msg=Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
    # Thread(target=sendAsyncEmail, args=(app, msg)).start()