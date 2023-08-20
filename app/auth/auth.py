from flask import Blueprint, render_template, url_for, request, redirect
from .forms import RegisterForm, ParticipantLoginForm
from ..models import Login, Participant
import uuid
from app import db, bcrypt
from flask_login import login_user

auth_bp = Blueprint('auth', __name__, template_folder="templates", static_folder="static", static_url_path='static')

@auth_bp.route('/participant', methods=['GET', 'POST'])
def participantLogin():
    form = ParticipantLoginForm()

    if request.method == "POST":
        if form.validate_on_submit():
            attempted_user = Login.query.get(form.email.data).first()
            if attempted_user and bcrypt.check_password_hash(attempted_user.password, form.password.data):
                login_user(attempted_user)
                return redirect(url_for('auth.logout')) # temp route
            else:
                # Wrong credentials
                pass

    return render_template('auth/participant/parti_login.html', form=form)

@auth_bp.route('/participant/signup', methods=['GET', 'POST'])
def participantSignup():
    form = RegisterForm()
    
    if request.method == "POST":
        if form.validate_on_submit():
            login_uuid = uuid.uuid4()
            hashed_password = bcrypt.generate_password_hash(form.password1.data).decode('utf-8')
            parti_login = Login(id=login_uuid,
                                email=form.email.data,
                                password=hashed_password,
                                role_id=2)
            parti_to_create = Participant(id=uuid.uuid4(),
                                        first_name=form.first_name.data,
                                        middle_name=form.middle_name.data,
                                        last_name=form.last_name.data,
                                        contact_details=form.contact_details.data,
                                        birthdate=form.birthdate.data,
                                        gender=form.gender.data,
                                        address=form.address.data,
                                        login_id=login_uuid)
            db.session.add(parti_login)
            db.session.add(parti_to_create)
            db.session.commit()
            return redirect(url_for('auth.participantLogin'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                print(err_msg)
    return render_template('auth/participant/parti_signup.html', form=form)

@auth_bp.route('/volunteer')
def volunteerLogin():
    pass

@auth_bp.route('/volunteer/signup')
def volunteerSignup():
    pass

@auth_bp.route('/logout')
def logout():
    return "Use this to log out"