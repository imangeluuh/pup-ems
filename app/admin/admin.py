from flask import Blueprint, render_template, url_for, request, redirect, flash
from .forms import LoginForm, addProjectForm
from ..models import Login, ExtensionProgram, Beneficiary
from app import db
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
    pass

@login_required
@admin_bp.route('/projects', methods=['GET', 'POST'])
def projects():
    pass
    # form = addProjectForm()
    # # programs = ExtensionProgram.query.all()
    # # if request.method == "POST":
    # #     if form.validate_on_submit():
    # #         program_to_add = ExtensionProgram(name = form.program_name.data,
    # #                             status = form.status.data, 
    # #                             target_participant = form.target_participant.data,
    # #                             location = form.location.data,
    # #                             start_date = form.start_date.data,
    # #                             end_date = form.end_date.data,
    # #                             description = form.description.data,
    # #                             objectives = form.objectives.data,
    # #                             expected_outcome = form.expected_outcome.data,
    # #                             terms_conditions = form.terms_conditions.data)
    # #         db.session.add(program_to_add)
    # #         db.session.commit()
    # #         return redirect(url_for('admin.projects'))
    #     if form.errors != {}: # If there are errors from the validations
    #         for err_msg in form.errors.values():
    #             flash(err_msg)
    # return render_template('admin/program_management.html', programs=programs, form=form)

@login_required
@admin_bp.route('/beneficiaries')
def benificiaries():
    benificiaries = Beneficiary.query.all()
    return render_template('admin/benificiaries.html', benificiaries=benificiaries)