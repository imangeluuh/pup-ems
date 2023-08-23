from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, current_user

projects_bp = Blueprint('projects', __name__, template_folder="templates", static_folder="static", static_url_path='static')

@projects_bp.route('/projects')
def projectsList():
    return render_template('projects/projects_list.html')