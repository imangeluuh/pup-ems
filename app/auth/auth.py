from app.auth import bp
from flask import render_template, url_for, request, redirect, flash
from .forms import BeneficiaryRegisterForm, StudentRegisterForm, LoginForm
from ..models import Login, Beneficiary, User, Student
import uuid
from app import db
from flask_login import login_user, logout_user, current_user
from datetime import datetime, timedelta

lockout_duration = timedelta(minutes=1)

@bp.route('/beneficiary', methods=['GET', 'POST'])
# @limiter.limit('5 per day')
# @limiter.limit("3 per day", key_func=lambda: request.method == "POST")
def beneficiaryLogin():
    # Prevents logged in users from accessing the page
    current_url_path = request.path
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # Temp route
    
    form = LoginForm()

    if request.method == "POST":
        if form.validate_on_submit():
            attempted_user = Login.query.filter_by(Email=form.email.data).first()
            if attempted_user and attempted_user.RoleId == 2:
                if attempted_user.check_password_correction(attempted_password=form.password.data):
                    login_user(attempted_user, remember=True)
                    return redirect(url_for('home')) # temp route
                else:
                    flash('The password you\'ve entered is incorrect.')
            else:
                flash('The email you entered isn\'t connected to an account.')

    return render_template('auth/beneficiary/beneficiary_login.html', form=form, current_url_path=current_url_path)

@bp.route('/beneficiary/signup', methods=['GET', 'POST'])
def beneficiarySignup():
    current_url_path = request.path
    form = BeneficiaryRegisterForm()    
    current_url_path = request.path
    if request.method == "POST":
        if form.validate_on_submit():
            str_user_id = createUser(form, 2)
            beneficiary_to_create = Beneficiary(BeneficiaryId = str_user_id)
            db.session.add(beneficiary_to_create)
            db.session.commit()
            return redirect(url_for('auth.beneficiaryLogin'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg)
    return render_template('auth/beneficiary/beneficiary_signup.html', form=form, current_url_path=current_url_path)

@bp.route('/student', methods=['GET', 'POST'])
def studentLogin():
    current_url_path = request.path
    # Prevents logged in users from accessing the page
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # Temp route
    
    form = LoginForm()

    if request.method == "POST":
        if form.validate_on_submit():
            attempted_user = Login.query.filter_by(Email=form.email.data).first()
            if attempted_user and attempted_user.RoleId == 3:
                if attempted_user.check_password_correction(attempted_password=form.password.data):
                    login_user(attempted_user, remember=True)
                    return redirect(url_for('home')) # temp route
                else:
                    flash('The password you\'ve entered is incorrect.')
            else:
                flash('The email you entered isn\'t connected to an account.')

    return render_template('auth/student/student_login.html', form=form, current_url_path=current_url_path)

@bp.route('/student/signup', methods=['GET', 'POST'])
def studentSignup():
    current_url_path = request.path
    form = StudentRegisterForm()    
    current_url_path = request.path
    if request.method == "POST":
        if form.validate_on_submit():
            str_user_id = createUser(form, 3)
            student_to_create = Student(StudentId = str_user_id,
                                        SkillsInterest = form.skills_interest.data)
            db.session.add(student_to_create)
            db.session.commit()
            return redirect(url_for('auth.studentLogin'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg)
    return render_template('auth/student/student_signup.html', form=form, current_url_path=current_url_path)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home')) # temp route

def createUser(form, role):
    str_login_uuid = uuid.uuid4()
    user_login = Login(LoginId=str_login_uuid,
                        Email=form.email.data,
                        password_hash=form.password1.data,
                        RoleId=role)
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
