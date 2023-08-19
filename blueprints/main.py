from flask import Blueprint, render_template, url_for

main = Blueprint('main', __name__)

@main.route("/greet")
def index():
    return render_template('greet.html')

