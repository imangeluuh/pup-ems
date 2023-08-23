from flask import Blueprint, render_template, url_for, request, redirect, flash
from .forms import RegisterForm, ParticipantLoginForm
from ..models import Login, Participant, User
import uuid
from app import db
from flask_login import login_user, logout_user, current_user

auth_bp = Blueprint('auth', __name__, template_folder="templates", static_folder="static", static_url_path='static')

@auth_bp.route('/participant', methods=['GET', 'POST'])
def participantLogin():
    # Prevents logged in users from accessing the page
    if current_user.is_authenticated:
        return render_template('greet.html')  # Temp route
    
    form = ParticipantLoginForm()

    if request.method == "POST":
        if form.validate_on_submit():
            attempted_user = Login.query.filter_by(email=form.email.data).first()
            if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
                login_user(attempted_user)
                return render_template('greet.html') # temp route
            else:
                flash('Incorrect email or password.')

    return render_template('auth/participant/parti_login.html', form=form)

@auth_bp.route('/participant/signup', methods=['GET', 'POST'])
def participantSignup():
    form = RegisterForm()    
    if request.method == "POST":
        if form.validate_on_submit():
            user_id = create_user(form)
            parti_to_create = Participant(id = user_id)
            db.session.add(parti_to_create)
            db.session.commit()
            return redirect(url_for('auth.participantLogin'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg)
    return render_template('auth/participant/parti_signup.html', form=form)

@auth_bp.route('/volunteer')
def volunteerLogin():
    pass

@auth_bp.route('/volunteer/signup')
def volunteerSignup():
    pass

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.participantLogin')) # temp route

def create_user(form):
    login_uuid = uuid.uuid4()
    user_login = Login(id=login_uuid,
                        email=form.email.data,
                        password_hash=form.password1.data,
                        role_id=2)
    user_id = uuid.uuid4()
    user_to_create = User(id=user_id,
                            first_name=form.first_name.data,
                            middle_name=form.middle_name.data,
                            last_name=form.last_name.data,
                            contact_details=form.contact_details.data,
                            birthdate=form.birthdate.data,
                            gender=form.gender.data,
                            address=form.address.data,
                            login_id=login_uuid)
    db.session.add(user_login)
    db.session.add(user_to_create)
    db.session.commit()
    return user_id
