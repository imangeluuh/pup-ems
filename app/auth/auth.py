from flask import Blueprint, render_template, url_for, request, redirect, flash
from .forms import RegisterForm, BeneficiaryLoginForm
from ..models import Login, Beneficiary, User
import uuid
from app import db
from flask_login import login_user, logout_user, current_user
from datetime import datetime, timedelta


auth_bp = Blueprint('auth', __name__, template_folder="templates", static_folder="static", static_url_path='static')

lockout_duration = timedelta(minutes=1)


@auth_bp.route('/beneficiary', methods=['GET', 'POST'])
# @limiter.limit('5 per day')
# @limiter.limit("3 per day", key_func=lambda: request.method == "POST")
def beneficiaryLogin():
    # Prevents logged in users from accessing the page
    if current_user.is_authenticated:
        return render_template('greet.html')  # Temp route
    
    form = BeneficiaryLoginForm()

    if request.method == "POST":
        if form.validate_on_submit():
            attempted_user = Login.query.filter_by(Email=form.email.data).first()
            if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
                login_user(attempted_user, remember=True)
                return redirect(url_for('programs.projectsList')) # temp route
            else:
                flash('Incorrect email or password.')

    return render_template('auth/beneficiary/beneficiary_login.html', form=form)

@auth_bp.route('/beneficiary/signup', methods=['GET', 'POST'])
def beneficiarySignup():
    form = RegisterForm()    
    if request.method == "POST":
        if form.validate_on_submit():
            str_user_id = createUser(form)
            beneficiary_to_create = Beneficiary(BeneficiaryId = str_user_id)
            db.session.add(beneficiary_to_create)
            db.session.commit()
            return redirect(url_for('auth.beneficiaryLogin'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg)
    return render_template('auth/beneficiary/beneficiary_signup.html', form=form)

@auth_bp.route('/student')
def studentLogin():
    pass

@auth_bp.route('/student/signup')
def studentSignup():
    pass

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.beneficiaryLogin')) # temp route

def createUser(form):
    str_login_uuid = uuid.uuid4()
    user_login = Login(LoginId=str_login_uuid,
                        Email=form.email.data,
                        password_hash=form.password1.data,
                        RoleId=2)
    str_user_id = uuid.uuid4()
    user_to_create = User(UserId=str_user_id,
                            FirstName=form.first_name.data,
                            MiddleName=form.middle_name.data,
                            LastName=form.last_name.data,
                            ContactDetails=form.contact_details.data,
                            Birthdate=form.birthdate.data,
                            Gender=form.gender.data,
                            Address=form.address.data,
                            LoginId=str_login_uuid)
    db.session.add(user_login)
    db.session.add(user_to_create)
    db.session.commit()
    return str_user_id
