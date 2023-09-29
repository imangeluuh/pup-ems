from app.admin import bp
from flask import render_template, url_for, request, redirect, flash, session
from flask_login import current_user, login_user, login_required, logout_user
from .forms import LoginForm, ProgramForm, ProjectForm, AnnouncementForm, ActivityForm
from ..models import Login, ExtensionProgram, Beneficiary, Project, Program, Student, Announcement, Registration, Activity, User
from ..Api.resources import AdminLoginApi
from ..decorators.decorators import login_required
from app import db, api, app
from ..store import uploadImage, purgeImage
from ..email import sendEmail
from werkzeug.utils import secure_filename
import string, requests, os
import datetime

headers = {"Content-Type": "application/json"}

@bp.route('/', methods=['GET', 'POST'])
def adminLogin():
    form = LoginForm()
    
    # Prevents logged in users from accessing the page
    if current_user.is_authenticated:
        return redirect(url_for('admin.programs'))  # Temp route
    
    if request.method == "POST":
        if form.validate_on_submit():
            data={'Email': form.email.data,
                'Password': form.password.data}
            response = requests.post(api.url_for(AdminLoginApi, _external=True), json=data, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                session['access_token'] = response_data.get('access_token')
                instance_user = Login()
                instance_user.set_user_data(login_data=response_data['admin'])
                login_user(instance_user, remember=True)
                return redirect(url_for('admin.programs')) # Temp route
            else:
                response_data = response.json()
                flash(response_data.get('error'))
    return render_template('admin/admin_login.html', form=form)

@bp.route('/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('admin.adminLogin'))

@bp.route('/home')
@login_required(role=["Admin"])
def home():
    pass

@bp.route('/programs')
@login_required(role=["Admin"])
def programs():
    form = ProgramForm()
    project_form = ProjectForm()
    programs = ExtensionProgram.query.all()
    projects = Project.query.all()
    
    return render_template('admin/program_management.html', programs=programs, projects=projects, form=form, project_form=project_form)

def saveImage(image, imagepath):
    imagename = secure_filename(image.filename)
    image.save(imagepath)
    # Upload image to imagekit
    return uploadImage(imagepath, imagename)

@bp.route('/extension-program/insert', methods=['POST'])
@login_required(role=["Admin"])
def insertExtensionProgram():
    form = ProgramForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if form.image.data is not None:
                # Get the input image path
                imagepath = os.path.join(
                        app.config["UPLOAD_FOLDER"], secure_filename(form.image.data.filename)
                    )
                # Save image
                status = saveImage(form.image.data, imagepath)
                if status.error is not None:
                    flash("File Upload Error")
                    return redirect(url_for('admin.programs'))
                else:
                    str_image_url = status.url
                    str_image_file_id = status.file_id
                program_to_add = ExtensionProgram(Name = form.program_name.data,
                                    Status = form.status.data, 
                                    AgendaId = form.agenda.data,
                                    ProgramId = form.program.data,
                                    DateApproved = form.date_approved.data,
                                    ImplementationDate = form.implementation_date.data,
                                    ImageUrl=str_image_url,
                                    ImageFileId=str_image_file_id)
                db.session.add(program_to_add)
                db.session.commit()
                flash('Extension progam is successfully inserted.', category='success')
            # Delete file from local storage
            if os.path.exists(imagepath):
                os.remove(imagepath)
            return redirect(url_for('admin.programs'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg, category='error')
    return redirect(url_for('admin.programs'))


@bp.route('/update/extension-program/<int:id>', methods=['POST'])
@login_required(role=["Admin"])
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
                    app.config["UPLOAD_FOLDER"], secure_filename(form.image.data.filename)
                )
            # Save image
            status = saveImage(form.image.data, imagepath)
            if status.error is not None:
                flash("File Upload Error")
                return redirect(url_for('admin.programs'))
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

        return redirect(url_for('admin.programs'))
    
    if form.errors != {}: # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(err_msg)

    return redirect(url_for('admin.programs'))


@bp.route('/delete/extension-program/<int:id>', methods=['POST'])
@login_required(role=["Admin"])
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

    return redirect(url_for('admin.programs'))


@bp.route('/extension-program/project/insert', methods=['POST'])
@login_required(role=["Admin"])
def insertProject():
    form = ProjectForm()
    if request.method == "POST":
        if form.validate_on_submit():
            str_image_url = None
            str_image_file_id = None
            if form.image.data is not None:
                # Get the input image path
                imagepath = os.path.join(
                        app.config["UPLOAD_FOLDER"], secure_filename(form.image.data.filename)
                    )
                # Save image
                status = saveImage(form.image.data, imagepath)
                if status.error is not None:
                    flash("File Upload Error")
                    return redirect(url_for('admin.programs'))
                else:
                    str_image_url = status.url
                    str_image_file_id = status.file_id
            project_to_add = Project(Name = form.project_name.data,
                                LeadProponent = form.lead_proponent.data, 
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
            # Delete file from local storage
            if os.path.exists(imagepath):
                os.remove(imagepath)
            flash('Extension project is successfully inserted.', category='success')
            return redirect(url_for('admin.programs'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg, category='error')
    return redirect(url_for('admin.programs'))


@bp.route('/project/<int:id>', methods=['GET', 'POST'])
@login_required(role=["Admin"])
def viewProject(id):
    form = ProjectForm()
    activity_form = ActivityForm()
    project = Project.query.get_or_404(id)
    registered = Registration.query.filter_by(ProjectId=project.ProjectId)
    # for calendar - temp
    events = fetch_activities(id)
    
    form.lead_proponent.data = project.LeadProponent
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
@login_required(role=["Admin"])
def updateProject(id):
    form = ProjectForm()
    extension_project = Project.query.get_or_404(id)
    if form.validate_on_submit():
        if form.image.data is not None:
            # If extension project has previous image, remove it from imagekit
            if extension_project.ImageFileId is not None:
                status = purgeImage(extension_project.ImageFileId)
            # Get the input image path
            imagepath = os.path.join(
                    app.config["UPLOAD_FOLDER"], secure_filename(form.image.data.filename)
                )
            # Save image
            status = saveImage(form.image.data, imagepath)
            if status.error is not None:
                flash("File Upload Error")
                return redirect(url_for('admin.programs'))
            else:
                extension_project.ImageUrl = status.url
                extension_project.ImageFileId = status.file_id
            # Delete file from local storage
            if os.path.exists(imagepath):
                os.remove(imagepath)
        extension_project.Name = form.project_name.data
        extension_project.LeadProponent= form.lead_proponent.data
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

        return redirect(url_for('admin.viewProject', id=extension_project.ProjectId))
    
    if form.errors != {}: # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(err_msg)

    return redirect(url_for('admin.viewProject', id=extension_project.ProjectId))


@bp.route('/delete/project/<int:id>', methods=['POST'])
@login_required(role=["Admin"])
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

    return redirect(url_for('admin.programs'))

@bp.route('/activity/create', methods=['POST'])
@login_required(role=["Admin"])
def insertActivity():
    form = ActivityForm()
    if form.validate_on_submit():
        str_image_url = None
        str_image_file_id = None
        if form.image.data is not None:
            # Get the input image path
            imagepath = os.path.join(
                    app.config["UPLOAD_FOLDER"], secure_filename(form.image.data.filename)
                )
            # Save image
            status = saveImage(form.image.data, imagepath)
            if status.error is not None:
                flash("File Upload Error")
                return redirect(url_for('admin.viewProject', id=form.project.data))
            else:
                str_image_url = status.url
                str_image_file_id = status.file_id
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
        return redirect(url_for('admin.viewProject', id=form.project.data))
    if form.errors != {}: # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(err_msg, category='error')
    return redirect(url_for('admin.viewProject', id=form.project.data))

@bp.route('/activity/<int:id>', methods=['POST'])
@login_required(role=["Admin"])
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
                    app.config["UPLOAD_FOLDER"], secure_filename(form.image.data.filename)
                )
            # Save image
            status = saveImage(form.image.data, imagepath)
            if status.error is not None:
                flash("File Upload Error")
                return redirect(url_for('admin.programs'))
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
        return redirect(url_for('admin.viewProject', id=activity.ProjectId))
    if form.errors != {}: # If there are errors from the validations
        for field, error in form.errors.items():
             flash(f"Field '{field}' has an error: {error}", category='error')
    return redirect(url_for('admin.viewProject', id=activity.ProjectId))

@bp.route('/delete/activity/<int:id>', methods=['POST'])
@login_required(role=["Admin"])
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

    return redirect(url_for('admin.viewProject', id=project_id))

@bp.route('/beneficiaries')
@login_required(role=["Admin"])
def beneficiaries():
    users = Beneficiary.query.all()
    current_url_path = request.path
    return render_template('admin/users.html', users=users,current_url_path=current_url_path)

@bp.route('/students')
@login_required(role=["Admin"])
def students():
    users = Student.query.all()
    current_url_path = request.path
    return render_template('admin/users.html', users=users,current_url_path=current_url_path)


@bp.route('/calendar')
@login_required(role=["Admin"])
def calendar():
    projects = Project.query.all()
    selected_project_id = request.args.get('project_id', None)
    # Call a function to fetch activities based on the selected project
    activities = fetch_activities(selected_project_id)
    
    return render_template('admin/activity_calendar.html', projects=projects, events=activities, selected_project_id=selected_project_id)


@bp.route('/announcement/<string:project>')
@bp.route('/announcement', defaults={'project': None})
@login_required(role=["Admin"])
def announcement(project):
    page = request.args.get('page', 1, type=int)
    if project is not None:
        project_id = Project.query.filter_by(Name=project).first()
        published_announcements = Announcement.query.filter_by(IsLive=True, ProjectId=project_id.ProjectId).order_by(Announcement.Updated.desc()).paginate(page=page, per_page=3, error_out=False)
        draft_announcements = Announcement.query.filter_by(IsLive=False, ProjectId=project_id.ProjectId).order_by(Announcement.Updated.desc()).paginate(page=page, per_page=3, error_out=False)
    else:
        published_announcements = Announcement.query.filter_by(IsLive=True).order_by(Announcement.Updated.desc()).paginate(page=page, per_page=3, error_out=False)
        draft_announcements = Announcement.query.filter_by(IsLive=False).order_by(Announcement.Updated.desc()).paginate(page=page, per_page=3, error_out=False)
    
    published_next_url = url_for('admin.announcement', page=published_announcements.next_num) \
        if published_announcements.has_next else None
    published_prev_url = url_for('admin.announcement', page=published_announcements.prev_num) \
        if published_announcements.has_prev else None
    draft_next_url = url_for('admin.announcement', page=draft_announcements.next_num) \
        if draft_announcements.has_next else None
    draft_prev_url = url_for('admin.announcement', page=draft_announcements.prev_num) \
        if draft_announcements.has_prev else None
    
    programs = Program.query.all()
    return render_template('admin/announcement.html', programs=programs, published_announcements=published_announcements.items, \
                            draft_announcements=draft_announcements, published_next_url=published_next_url, published_prev_url=published_prev_url, \
                                draft_next_url=draft_next_url, draft_prev_url=draft_prev_url)


@bp.route('/announcement/create', methods=['GET', 'POST'])
@login_required(role=["Admin"])
def createAnnouncement():
    form = AnnouncementForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if 'publish' in request.form:
                if not all(request.form.values()):
                    # Save the input to session
                    session['announcement_title']= form.title.data
                    session['announcement_body'] = form.content.data
                    flash('Please fill out all the fields before publishing.')
                    return redirect(url_for('admin.createAnnouncement'))
                is_live = 1
            elif 'draft' in request.form:
                is_live = 0
            admin_login = current_user.AdminLogin
            announcement_to_create = Announcement(Title=form.title.data,
                                                Content=form.content.data,
                                                CreatorId=admin_login[0].AdminId,
                                                IsLive=is_live,
                                                Slug=generateSlug(form.title.data),
                                                ProjectId=form.project.data)
            db.session.add(announcement_to_create)
            db.session.commit()
            # If announcement session is not empty, clear the session after saving to database
            if 'announcement_title' in session:
                session.pop('announcement_title', None)
            if 'announcement_body' in session:
                session.pop('announcement_body', None)
            # If Email checkbox is checked, send the announcement to desired recipients
            if 'Email' in form.medium.data and form.recipient.data is not [] and is_live == 1:
                if len(form.recipient.data) == 2:
                    emails = (
                        User.query
                        .join(Registration)
                        .join(Project)
                        .join(Login, User.LoginId == Login.LoginId)
                        .filter(Project.ProjectId == 10)
                        .with_entities(Login.Email)
                        .all()
                    )
                else:
                    emails = (
                        User.query
                        .join(Registration)
                        .join(Project)
                        .join(Login, User.LoginId == Login.LoginId)
                        .filter(Project.ProjectId == 10, Login.RoleId == form.recipient.data[0])
                        .with_entities(Login.Email)
                        .all()
                    )
                # Extract the emails from the query result
                list_email = [email for (email,) in emails]
                sendEmail(form.title.data, list_email, form.content.data, form.content.data)
                flash('Announcement is successfully sent to email', category='success')
            flash('Announcement is successfully inserted.', category='success')
            return redirect(url_for('admin.announcement'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg, category='error')
    if 'announcement_title' in session:
        form.title.data = session['announcement_title']
    if 'announcement_body' in session:
        form.content.data = session['announcement_body']
    return render_template('admin/create_announcement.html', form=form)


@bp.route('/announcement/update/<int:id>', methods=['GET', 'POST'])
@login_required(role=["Admin"])
def updateAnnouncement(id):
    form = AnnouncementForm()
    announcement = Announcement.query.get_or_404(id)
    current_url_path = request.path

    if request.method == "POST":
        if form.validate_on_submit():
            if 'publish' in request.form:
                if not all(request.form.values()):
                    flash('Please fill out all the fields before publishing.')
                    return redirect(url_for('admin.updateAnnouncement'))
                is_live = 1
            elif 'draft' in request.form:
                is_live = 0

            announcement.Title=form.title.data
            announcement.Content=form.content.data
            announcement.IsLive=is_live
            announcement.Slug=generateSlug(form.title.data)

            try:
                db.session.commit()
                flash('Announcement is successfully updated.', category='success')
            except Exception as e:
                flash('There was an issue updating the announcement.', category='error')

            return redirect(url_for('admin.announcement'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg, category='error')
    
    form.title.data = announcement.Title
    form.content.data = announcement.Content

    return render_template('admin/edit_announcement.html', form=form, announcement=announcement, current_url_path=current_url_path)


@bp.route('/delete/announcement/<int:id>', methods=['POST'])
@login_required(role=["Admin"])
def deleteAnnouncement(id):
    announcement = Announcement.query.get_or_404(id)
    try:
        db.session.delete(announcement)
        db.session.commit()
        flash('Announcement is successfully deleted.', category='success')
    except:
        flash('There was an issue deleting the announcement.', category='error')

    return redirect(url_for('admin.announcement'))


@bp.route('/unpublish/announcement/<int:id>', methods=['POST'])
@login_required(role=["Admin"])
def unpublishAnnouncement(id):
    announcement = Announcement.query.get_or_404(id)
    announcement.IsLive = 0
    try:
        db.session.commit()
        flash('Announcement is successfully unpublished.', category='success')
    except:
        flash('There was an issue unpublishing the announcement.', category='error')

    return redirect(url_for('admin.announcement'))


@bp.route('/view/announcement/<int:id>/<string:slug>')
@login_required(role=["Admin"])
def viewAnnouncement(id, slug):
    announcement = Announcement.query.filter_by(AnnouncementId=id, Slug=slug).first_or_404()
    return render_template('admin/view_announcement.html', announcement=announcement)

@bp.route('/beneficiaries/<string:id>')
@login_required(role=["Admin"])
def viewUser(id):
    user = User.query.filter_by(UserId=id).first()
    user_projects = (
    Project.query
    .join(Registration, Registration.ProjectId == Project.ProjectId)
    .join(User, User.UserId == Registration.UserId)
    .filter(User.UserId == id)
    .all()
    )
    print(user_projects)
    return render_template('admin/view_user.html', user=user, user_projects=user_projects)


def generateSlug(title, separator='-', lower=True):
    title = title.translate(str.maketrans('', '', string.punctuation))
    if lower:
        title = title.lower()
    return separator.join(title.split())

# Define a new function to fetch activities based on the selected project
def fetch_activities(selected_project_id=None):

    query = Activity.query

    if selected_project_id:
        query = query.filter(Activity.ProjectId == selected_project_id)

    return query.with_entities(Activity.ActivityName, Activity.Date, Project.Name).join(Project).all()