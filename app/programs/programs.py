from app.programs import bp
from flask import render_template, url_for, request, redirect, flash, current_app
from flask_login import current_user
from ..models import Project, ExtensionProgram, Program, Registration, Agenda, ExtensionProgram, Activity
from .forms import ProgramForm, ProjectForm, ActivityForm, CombinedForm
import calendar
from datetime import datetime
from app import db, api
from ..store import uploadImage, purgeImage
from werkzeug.utils import secure_filename
import os, requests
from ..decorators.decorators import login_required
from ..Api.resources import ExtensionProgramListApi

# ============== Admin/Faculty views ===========================

@bp.route('/pupqc/extension-programs')
@login_required(role=["Admin", "Faculty"])
def programs():
    form = ProgramForm()
    project_form = ProjectForm()
    response = requests.get(api.url_for(ExtensionProgramListApi, _external=True))
    programs = None
    if response.status_code == 200:
        programs = response.json()
        print(programs)
    else:
        flash('Error')
    
    return render_template('admin/program_management.html', programs=programs, form=form, project_form=project_form)

def saveImage(image, imagepath):
    imagename = secure_filename(image.filename)
    image.save(imagepath)
    # Upload image to imagekit
    return uploadImage(imagepath, imagename)

@bp.route('/extension-program/insert', methods=['GET', 'POST'])
@login_required(role=["Admin", "Faculty"])
def insertExtensionProgram():
    form = CombinedForm()
    if request.method == 'POST':
        str_image_url = None
        str_image_file_id = None
        if form.extension_program.image.data is not None:
            # Get the input image path
            imagepath = os.path.join(
                    current_app.config["UPLOAD_FOLDER"], secure_filename(form.extension_program.image.data.filename)
                )
            # Save image
            status = saveImage(form.extension_program.image.data, imagepath)
            if status.error is not None:
                flash("Extension program image upload failed", category="error")
                return url_for('programs.addProgram')
            else:
                str_image_url = status.url
                str_image_file_id = status.file_id
            # Delete file from local storage
            if os.path.exists(imagepath):
                os.remove(imagepath)
        program_to_add = ExtensionProgram(Name = form.extension_program.program_name.data,
                            Status = form.extension_program.status.data, 
                            ProposedBudget = form.extension_program.proposed_budget.data,
                            ApprovedBudget = form.extension_program.approved_budget.data,
                            FundType = form.extension_program.fund_type.data,
                            AgendaId = form.extension_program.agenda.data,
                            ProgramId = form.extension_program.program.data,
                            CollaboratorId = form.extension_program.collaborator.data,
                            DateApproved = form.extension_program.date_approved.data,
                            ImplementationDate = form.extension_program.implementation_date.data,
                            ImageUrl=str_image_url,
                            ImageFileId=str_image_file_id)
        db.session.add(program_to_add)
        db.session.flush()
        int_program_id = program_to_add.ExtensionProgramId
        # Insert project
        str_image_url = None
        str_image_file_id = None
        if form.project.image.data is not None:
            # Get the input image path
            imagepath = os.path.join(
                    current_app.config["UPLOAD_FOLDER"], secure_filename(form.project.image.data.filename)
                )
            # Save image
            status = saveImage(form.project.image.data, imagepath)
            if status.error is not None:
                flash("Project image upload failed", category="error")
                return redirect(url_for('programs.addProgram'))
            else:
                str_image_url = status.url
                str_image_file_id = status.file_id
            # Delete file from local storage
            if os.path.exists(imagepath):
                os.remove(imagepath)
        lead_proponent = current_user.User[0]
        project_to_add = Project(Name = form.project.project_name.data,
                            LeadProponentId = lead_proponent.UserId,
                            ProjectType = form.project.project_type.data,
                            Rationale = form.project.rationale.data,
                            Objectives = form.project.objectives.data,
                            Status = form.project.status.data,
                            ImageUrl=str_image_url,
                            ImageFileId=str_image_file_id,
                            StartDate = form.project.start_date.data,
                            NumberOfBeneficiaries = form.project.num_of_beneficiaries.data,
                            BeneficiariesClassifications = form.project.beneficiaries_classifications.data,
                            ProjectScope = form.project.project_scope.data,
                            ExtensionProgramId = int_program_id)
        db.session.add(project_to_add)
        db.session.flush()
        int_project_id = project_to_add.ProjectId
        # Insert Activity
        str_image_url = None
        str_image_file_id = None
        if form.activity.image.data is not None:
            # Get the input image path
            imagepath = os.path.join(
                    current_app.config["UPLOAD_FOLDER"], secure_filename(form.activity.image.data.filename)
                )
            # Save image
            status = saveImage(form.activity.image.data, imagepath)
            if status.error is not None:
                flash("Activity image upload failed", category="error")
                return redirect(url_for('programs.addProgram'))
            else:
                str_image_url = status.url
                str_image_file_id = status.file_id
            # Delete file from local storage
            if os.path.exists(imagepath):
                os.remove(imagepath)
        activity_to_create = Activity(ActivityName=form.activity.activity_name.data,
                                        Date=form.activity.date.data,
                                        StartTime=form.activity.start_time.data,
                                        EndTime=form.activity.end_time.data,
                                        Description=form.activity.activity_description.data,
                                        ProjectId=int_project_id,
                                        ImageUrl=str_image_url,
                                        ImageFileId=str_image_file_id)
        db.session.add(activity_to_create)
        db.session.commit()
        return redirect(url_for('programs.programs'))
    if form.errors != {}: # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(err_msg, category='error')

    return render_template('programs/add_ext_program.html', form=form)


@bp.route('/extension-program/update/<int:id>', methods=['POST'])
@login_required(role=["Admin", "Faculty"])
def updateExtensionProgram(id):
    form = ProgramForm()
    extension_program = ExtensionProgram.query.get_or_404(id)
    if form.validate_on_submit():
        if form.image.data is not None:
            # If extension program has previous image, remove it from imagekit
            if extension_program.ImageFileId is not None:
                status = purgeImage(extension_program.ImageFileId)
            # Get the input image path
            imagepath = os.path.join(
                    current_app.config["UPLOAD_FOLDER"], secure_filename(form.image.data.filename)
                )
            # Save image
            status = saveImage(form.image.data, imagepath)
            if status.error is not None:
                flash("File Upload Error")
                return redirect(url_for('programs.programs'))
            else:
                extension_program.ImageUrl = status.url
                extension_program.ImageFileId = status.file_id
            # Delete file from local storage
            if os.path.exists(imagepath):
                os.remove(imagepath)
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

        return redirect(url_for('programs.programs'))
    
    if form.errors != {}: # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(err_msg)

    return redirect(url_for('programs.programs'))


@bp.route('/extension-program/delete/<int:id>', methods=['POST'])
@login_required(role=["Admin", "Faculty"])
def deleteExtensionProgram(id):
    extension_program = ExtensionProgram.query.get_or_404(id)
    try:
        if extension_program.ImageFileId is not None:
            status = purgeImage(extension_program.ImageFileId)
        db.session.delete(extension_program)
        db.session.commit()
        flash('Extension program is successfully deleted.', category='success')
    except:
        flash('There was an issue deleting the extension program.', category='error')

    return redirect(url_for('programs.programs'))


@bp.route('/extension-program/project/insert', methods=['POST'])
@login_required(role=["Admin", "Faculty"])
def insertProject():
    form = ProjectForm()
    if request.method == "POST":
        if form.validate_on_submit():
            str_image_url = None
            str_image_file_id = None
            if form.image.data is not None:
                # Get the input image path
                imagepath = os.path.join(
                        current_app.config["UPLOAD_FOLDER"], secure_filename(form.image.data.filename)
                    )
                # Save image
                status = saveImage(form.image.data, imagepath)
                if status.error is not None:
                    flash("File Upload Error")
                    return redirect(url_for('programs.programs'))
                else:
                    str_image_url = status.url
                    str_image_file_id = status.file_id

                # Delete file from local storage
                if os.path.exists(imagepath):
                    os.remove(imagepath)
            lead_proponent = current_user.User[0]
            project_to_add = Project(Name = form.project_name.data,
                                LeadProponentId = lead_proponent.UserId,
                                ProjectType = form.project_type.data,
                                Rationale = form.rationale.data,
                                Objectives = form.objectives.data,
                                Status = form.status.data,
                                ImageUrl=str_image_url,
                                ImageFileId=str_image_file_id,
                                StartDate = form.start_date.data,
                                NumberOfBeneficiaries = form.num_of_beneficiaries.data,
                                BeneficiariesClassifications = form.beneficiaries_classifications.data,
                                ProjectScope = form.project_scope.data,
                                ExtensionProgramId = form.extension_program.data)
            db.session.add(project_to_add)
            db.session.commit()
            flash('Extension project is successfully inserted.', category='success')
            return redirect(url_for('programs.programs'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg, category='error')
    return redirect(url_for('programs.programs'))


@bp.route('/project/<int:id>', methods=['GET', 'POST'])
@login_required(role=["Admin", "Faculty"])
def viewProject(id):
    form = ProjectForm()
    activity_form = ActivityForm()
    project = Project.query.get_or_404(id)
    registered = Registration.query.filter_by(ProjectId=project.ProjectId)
    # for calendar - temp
    events = fetch_activities(id)
    
    form.project_type.data = project.ProjectType
    form.project_name.data = project.Name
    form.rationale.data = project.Rationale
    form.objectives.data = project.Objectives
    form.status.data = project.Status
    form.start_date.data = project.StartDate
    form.num_of_beneficiaries.data = project.NumberOfBeneficiaries
    form.beneficiaries_classifications.data = project.BeneficiariesClassifications
    form.project_scope.data = project.ProjectScope
    form.extension_program.data = project.ExtensionProgramId

    return render_template('admin/view_project.html', project=project, form=form, activity_form=activity_form, registered=registered, events=events)


@bp.route('/project/update/<int:id>', methods=['POST'])
@login_required(role=["Admin", "Faculty"])
def updateProject(id):
    form = ProjectForm()
    extension_project = Project.query.get_or_404(id)
    if form.validate_on_submit():
        if form.image.data is not None:
            # If extension project has previous image, remove it from imagekit
            if extension_project.ImageFileId is not None:
                try:
                    status = purgeImage(extension_project.ImageFileId)
                except:
                    print("image not found")
            # Get the input image path
            imagepath = os.path.join(
                    current_app.config["UPLOAD_FOLDER"], secure_filename(form.image.data.filename)
                )
            # Save image
            status = saveImage(form.image.data, imagepath)
            if status.error is not None:
                flash("File Upload Error")
                return redirect(url_for('programs.programs'))
            else:
                extension_project.ImageUrl = status.url
                extension_project.ImageFileId = status.file_id
            # Delete file from local storage
            if os.path.exists(imagepath):
                os.remove(imagepath)
        extension_project.Name = form.project_name.data
        extension_project.ProjectType = form.project_type.data
        extension_project.Rationale = form.rationale.data
        extension_project.Objectives = form.objectives.data
        extension_project.Status = form.status.data
        extension_project.StartDate = form.start_date.data
        extension_project.NumberOfBeneficiaries = form.num_of_beneficiaries.data
        extension_project.BeneficiariesClassifications = form.beneficiaries_classifications.data
        extension_project.ProjectScope = form.project_scope.data

        try:
            db.session.commit()
            flash('Extension project is successfully updated.', category='success')
        except:
            flash('There was an issue updating the extension project.', category='error')

        return redirect(url_for('programs.viewProject', id=extension_project.ProjectId))
    
    if form.errors != {}: # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(err_msg)

    return redirect(url_for('programs.viewProject', id=extension_project.ProjectId))


@bp.route('/delete/project/<int:id>', methods=['POST'])
@login_required(role=["Admin", "Faculty"])
def deleteProject(id):
    project = Project.query.get_or_404(id)
    try:
        if project.ImageFileId is not None:
            status = purgeImage(project.ImageFileId)
        db.session.delete(project)
        db.session.commit()
        flash('Extension project is successfully deleted.', category='success')
    except Exception as e:
        flash('There was an issue deleting the extension project.', category='error')

    return redirect(url_for('programs.programs'))

@bp.route('/activity/create', methods=['POST'])
@login_required(role=["Admin", "Faculty"])
def insertActivity():
    form = ActivityForm()
    if form.validate_on_submit():
        str_image_url = None
        str_image_file_id = None
        if form.image.data is not None:
            # Get the input image path
            imagepath = os.path.join(
                    current_app.config["UPLOAD_FOLDER"], secure_filename(form.image.data.filename)
                )
            # Save image
            status = saveImage(form.image.data, imagepath)
            if status.error is not None:
                flash("File Upload Error")
                return redirect(url_for('programs.viewProject', id=form.project.data))
            else:
                str_image_url = status.url
                str_image_file_id = status.file_id

            # Delete file from local storage
            if os.path.exists(imagepath):
                os.remove(imagepath)
                
        activity_to_create = Activity(ActivityName=form.name.data,
                                        Date=form.date.data,
                                        StartTime=form.start_time.data,
                                        EndTime=form.end_time.data,
                                        Description=form.description.data,
                                        ProjectId=form.project.data,
                                        ImageUrl=str_image_url,
                                        ImageFileId=str_image_file_id)
        db.session.add(activity_to_create)
        db.session.commit()
        flash('Activity is successfully inserted.', category='success')
        return redirect(url_for('programs.viewProject', id=form.project.data))
    if form.errors != {}: # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(err_msg, category='error')
    return redirect(url_for('programs.viewProject', id=form.project.data))

@bp.route('/activity/<int:id>', methods=['POST'])
@login_required(role=["Admin", "Faculty"])
def updateActivity(id):
    form = ActivityForm()
    activity = Activity.query.filter_by(ActivityId=id).first()
    if form.validate_on_submit():
        if form.image.data is not None:
            # If extension project has previous image, remove it from imagekit
            if activity.ImageFileId is not None:
                status = purgeImage(activity.ImageFileId)
            # Get the input image path
            imagepath = os.path.join(
                    current_app.config["UPLOAD_FOLDER"], secure_filename(form.image.data.filename)
                )
            # Save image
            status = saveImage(form.image.data, imagepath)
            if status.error is not None:
                flash("File Upload Error")
                return redirect(url_for('programs.programs'))
            else:
                activity.ImageUrl = status.url
                activity.ImageFileId = status.file_id
            # Delete file from local storage
            if os.path.exists(imagepath):
                os.remove(imagepath)
        activity.ActivityName=form.name.data
        activity.Date=form.date.data
        activity.Description=form.description.data
        activity.StartTime=form.start_time.data
        activity.EndTime=form.end_time.data
        db.session.commit()
        flash('Activity is successfully updated.', category='success')
        return redirect(url_for('programs.viewProject', id=activity.ProjectId))
    if form.errors != {}: # If there are errors from the validations
        for field, error in form.errors.items():
            flash(f"Field '{field}' has an error: {error}", category='error')
    return redirect(url_for('programs.viewProject', id=activity.ProjectId))

@bp.route('/delete/activity/<int:id>', methods=['POST'])
@login_required(role=["Admin", "Faculty"])
def deleteActivity(id):
    activity = Activity.query.get_or_404(id)
    project_id = activity.ProjectId
    try:
        if activity.ImageFileId is not None:
            status = purgeImage(activity.ImageFileId)
        db.session.delete(activity)
        db.session.commit()
        flash('Activity is successfully deleted.', category='success')
    except Exception as e:
        flash('There was an issue deleting the activity.', category='error')

    return redirect(url_for('programs.viewProject', id=project_id))



# ======================= User views ======================

@bp.route('/programs')
def programsList():
    extension_programs = ExtensionProgram.query.all()
    programs = Program.query.all()
    agendas = Agenda.query.all()
    return render_template('programs/programs.html', extension_programs=extension_programs, programs=programs, agendas=agendas)


@bp.route('/projects/<int:program_id>', methods=['GET', 'POST'])
def projectsList(program_id):
    extension_program = ExtensionProgram.query.filter_by(ExtensionProgramId=program_id).first()
    projects = Project.query.filter_by(ExtensionProgramId=program_id).all()
    return render_template('programs/projects_list.html', extension_program=extension_program, projects=projects)
    

@bp.route('/filters')
def filters():
    # Retrieve only the names from the program table
    extension_programs = ExtensionProgram.query.with_entities(ExtensionProgram.Name).all()
    programs = Program.query.with_entities(Program.ProgramName).all()

    # Convert the query result into a list of names
    list_extension_programs = [extension_program[0] for extension_program in extension_programs]
    list_programs = [program[0] for program in programs]

    # Get the current month
    current_month = datetime.now().month

    # Create a list of months from current month to December
    list_months = [calendar.month_name[i] for i in range(current_month, 13)]

    dict_filters = {
        'Extension Program': list_extension_programs,
        'Program': list_programs,
        'Month': list_months,
    }

    str_filter = request.args.get('filter')

    list_filter = dict_filters[str_filter]

    return render_template('programs/filters.html',list_filter=list_filter)


@bp.route('/registration/<int:project_id>', methods=['GET', 'POST'])
def registration(project_id):
    project = Project.query.get_or_404(project_id)
    user_id = current_user.UserLogin[0].UserId if current_user.is_authenticated else None
    bool_is_registered = True if Registration.query.filter_by(ProjectId=project_id, UserId=user_id).first() else False
    if request.method == 'POST':
        registration_to_create = Registration(ProjectId = project_id,
                                            UserId=user_id)
        try:
            db.session.add(registration_to_create)
            db.session.commit()
            flash('Registration Successful!', category='success')
        except  Exception as e:
            flash('There was an issue during registration.', category='error')

        return redirect(url_for('programs.registration', project_id=project_id))
    return render_template("programs/project_reg.html", project=project, bool_is_registered=bool_is_registered)


@bp.route('/registration/cancel/<int:project_id>', methods=['POST'])
def cancelRegistration(project_id):
    project = Project.query.get_or_404(project_id)
    user_id = current_user.UserLogin[0].UserId if current_user.is_authenticated else None
    registration = Registration.query.filter_by(ProjectId=project_id, UserId=user_id).first()

    try:
        db.session.delete(registration)
        db.session.commit()
        flash('Registration is successfully canceled.', category='success')
    except:
        flash('There was an issue canceling the registration.', category='error')

    return redirect(url_for('programs.registration', project_id=project_id))

# Define a new function to fetch activities based on the selected project
def fetch_activities(selected_project_id=None):

    query = Activity.query

    if selected_project_id:
        query = query.filter(Activity.ProjectId == selected_project_id)

    return query.with_entities(Activity.ActivityName, Activity.Date, Project.Name).join(Project).all()