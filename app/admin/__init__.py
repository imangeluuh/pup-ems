from flask import Blueprint

bp = Blueprint('admin', __name__, template_folder="templates", static_folder="static", static_url_path='static')

