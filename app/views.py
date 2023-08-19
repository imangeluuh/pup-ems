from app import app
from app.models import Role
from flask import render_template

@app.route("/")
def home():
    roles = Role.query.all()
    return render_template('index.html', roles=roles)