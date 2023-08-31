from flask import Blueprint, render_template, url_for, request, redirect, flash
from .forms import LoginForm, ProjectForm
from ..models import Login, ExtensionProgram, Beneficiary
from app import db
from datetime import date
from flask_login import current_user, login_user, login_required, logout_user

admin_bp = Blueprint('admin', __name__, template_folder="templates", static_folder="static", static_url_path='static')

@admin_bp.route('/', methods=['GET', 'POST'])
def adminLogin():
    form = LoginForm()
    
    # Prevents logged in users from accessing the page
    if current_user.is_authenticated:
        return render_template('greet.html')  # Temp route

    if request.method == "POST":
        if form.validate_on_submit():
            attempted_user = Login.query.filter_by(Email=form.email.data).first()
            if attempted_user and attempted_user.RoleId == 1: 
                if attempted_user.check_password_correction(attempted_password=form.password.data):
                    login_user(attempted_user, remember=True)
                    return redirect(url_for('admin.programs')) # temp route
                else:
                    flash('The password you\'ve entered is incorrect.')
            else:
                flash('The email you entered isn\'t connected to an account.')
    return render_template('admin/admin_login.html', form=form)

@admin_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.adminLogin'))

@login_required
@admin_bp.route('/home')
def home():
    pass

@login_required
@admin_bp.route('/programs')
def programs():
    # pass
    form = ProjectForm()
    programs = ExtensionProgram.query.all()
    
    return render_template('admin/program_management.html', programs=programs, form=form)


@login_required
@admin_bp.route('/extension-program/insert', methods=['POST'])
def insertExtensionProgram():
    form = ProjectForm()
    if request.method == "POST":
        if form.validate_on_submit():
            program_to_add = ExtensionProgram(Name = form.program_name.data,
                                Status = form.status.data, 
                                Agenda = form.agenda.data,
                                Program = form.program.data,
                                DateApproved = form.date_approved.data,
                                ImplementationDate = form.implementation_date.data,)
            db.session.add(program_to_add)
            db.session.commit()
            flash('Extension progam is successfully inserted.', category='success')
            return redirect(url_for('admin.programs'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg, category='error')
    return redirect(url_for('admin.programs'))


@login_required
@admin_bp.route('/update/extension-program/<int:id>', methods=['POST'])
def updateExtensionProgram(id):
    form = ProjectForm()
    extension_program = ExtensionProgram.query.get_or_404(id)
    if form.validate_on_submit():
        extension_program.Name = form.program_name.data
        extension_program.Status = form.status.data
        extension_program.Agenda = form.agenda.data
        extension_program.Program = form.program.data
        extension_program.DateApproved = form.date_approved.data
        extension_program.ImplementationDate = form.implementation_date.data

        try:
            db.session.commit()
            flash('Extension progam is successfully updated.', category='success')
        except:
            flash('There was an issue updating the extension program.', category='error')

        return redirect(url_for('admin.programs'))
    
    if form.errors != {}: # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(err_msg)

    return redirect(url_for('admin.programs'))


@login_required
@admin_bp.route('/delete/extension-program/<int:id>', methods=['POST'])
def deleteExtensionProgram(id):
    extension_program = ExtensionProgram.query.get_or_404(id)
    try:
        db.session.delete(extension_program)
        db.session.commit()
        flash('Extension program is successfully deleted.', category='success')
    except:
        flash('There was an issue deleting the extension program.', category='error')

    return redirect(url_for('admin.programs'))


@login_required
@admin_bp.route('/beneficiaries')
def beneficiaries():
    beneficiaries = Beneficiary.query.all()
    return render_template('admin/beneficiaries.html', beneficiaries=beneficiaries)


@admin_bp.route('/calendar')
def calendar():
    return render_template('admin/index.html')

