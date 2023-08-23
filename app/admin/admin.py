from flask import Blueprint, render_template, url_for, request, redirect, flash
from .forms import LoginForm
from ..models import Login
# from app import db
from flask_login import current_user, login_user, login_required

admin_bp = Blueprint('admin', __name__, template_folder="templates", static_folder="static", static_url_path='static')

@admin_bp.route('/', methods=['GET', 'POST'])
def adminLogin():
    form = LoginForm()
    
    # Prevents logged in users from accessing the page
    if current_user.is_authenticated:
        return render_template('greet.html')  # Temp route

    if request.method == "POST":
        if form.validate_on_submit():
            attempted_user = Login.query.filter_by(email=form.email.data).first()
            if attempted_user and attempted_user.role_id == 1: 
                if attempted_user.check_password_correction(attempted_password=form.password.data):
                    login_user(attempted_user)
                    return redirect(url_for('admin.projects')) # temp route
                else:
                    flash('The password you\'ve entered is incorrect.')
            else:
                flash('The email you entered isn\'t connected to an account.')
    return render_template('admin/admin_login.html', form=form)

@admin_bp.route('/logout')
def logout():
    return "Use this to log out"

@login_required
@admin_bp.route('/home')
def home():
    return render_template('')

@login_required
@admin_bp.route('/projects')
def projects():
    return render_template('admin/program_management.html')

@login_required
@admin_bp.route('/participants')
def participants():
    return render_template('admin/participants.html')