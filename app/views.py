from app import app
from app.models import Announcement, ExtensionProgram
from flask import render_template, request
from sqlalchemy import desc

@app.route("/")
def home():
    latest_announcements = Announcement.query.order_by(desc(Announcement.Updated)).limit(5).all()
    extension_programs = ExtensionProgram.query.all()
    return render_template('index.html', latest_announcements=latest_announcements, extension_programs=extension_programs)