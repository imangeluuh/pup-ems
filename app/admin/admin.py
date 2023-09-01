from flask import Blueprint, render_template, url_for, request, redirect, flash
from .forms import LoginForm, ProgramForm, ProjectForm
from ..models import Login, ExtensionProgram, Beneficiary, Project, Agenda, Program
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
    form = ProgramForm()
    project_form = ProjectForm()
    programs = ExtensionProgram.query.all()
    projects = Project.query.all()
    
    return render_template('admin/program_management.html', programs=programs, projects=projects, form=form, project_form=project_form)


@login_required
@admin_bp.route('/extension-program/insert', methods=['POST'])
def insertExtensionProgram():
    form = ProgramForm()
    if request.method == "POST":
        if form.validate_on_submit():
            program_to_add = ExtensionProgram(Name = form.program_name.data,
                                Status = form.status.data, 
                                AgendaId = form.agenda.data,
                                ProgramId = form.program.data,
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
    form = ProgramForm()
    extension_program = ExtensionProgram.query.get_or_404(id)
    if form.validate_on_submit():
        extension_program.Name = form.program_name.data
        extension_program.Status = form.status.data
        extension_program.AgendaId = int(form.agenda.data)
        extension_program.ProgramId = int(form.program.data)
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
@admin_bp.route('/extension-program/project/insert', methods=['POST'])
def insertProject():
    form = ProjectForm()
    if request.method == "POST":
        if form.validate_on_submit():
            project_to_add = Project(Name = form.project_name.data,
                                LeadProponent = form.lead_proponent.data, 
                                ProjectType = form.project_type.data,
                                Rationale = form.rationale.data,
                                Objectives = form.objectives.data,
                                StartDate = form.start_date.data,
                                NumberOfBeneficiaries = form.num_of_beneficiaries.data,
                                BeneficiariesClassifications = form.beneficiaries_classifications.data,
                                ProjectScope = form.project_scope.data,
                                ExtensionProgramId = form.extension_program.data)
            db.session.add(project_to_add)
            db.session.commit()
            flash('Extension project is successfully inserted.', category='success')
            return redirect(url_for('admin.programs'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg, category='error')
    return redirect(url_for('admin.programs'))


@login_required
@admin_bp.route('/update/extension-program/project/<int:id>', methods=['POST'])
def updateProject(id):
    form = ProjectForm()
    extension_project = Project.query.get_or_404(id)
    if form.validate_on_submit():
        extension_project.Name = form.project_name.data
        extension_project.LeadProponent= form.lead_proponent.data
        extension_project.ProjectType = form.project_type.data
        extension_project.Rationale = form.rationale.data
        extension_project.Objectives = form.objectives.data
        extension_project.StartDate = form.start_date.data
        extension_project.NumberOfBeneficiaries = form.num_of_beneficiaries.data
        extension_project.BeneficiariesClassifications = form.beneficiaries_classifications.data
        extension_project.ProjectScope = form.project_scope.data
        extension_project.ExtensionProgramId = form.extension_program.data

        try:
            db.session.commit()
            flash('Extension progaject is successfully updated.', category='success')
        except:
            flash('There was an issue updating the extension project.', category='error')

        return redirect(url_for('admin.programs'))
    
    if form.errors != {}: # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(err_msg)

    return redirect(url_for('admin.programs'))


@login_required
@admin_bp.route('/delete/extension-program/project/<int:id>', methods=['POST'])
def deleteProject(id):
    project = Project.query.get_or_404(id)
    try:
        db.session.delete(project)
        db.session.commit()
        flash('Extension project is successfully deleted.', category='success')
    except:
        flash('There was an issue deleting the extension project.', category='error')

    return redirect(url_for('admin.programs'))


@login_required
@admin_bp.route('/beneficiaries')
def beneficiaries():
    beneficiaries = Beneficiary.query.all()
    return render_template('admin/beneficiaries.html', beneficiaries=beneficiaries)


@admin_bp.route('/calendar')
def calendar():
    return render_template('admin/index.html')

