from flask import Blueprint, render_template, url_for, request, redirect, flash
from .forms import LoginForm, ProgramForm, ProjectForm, AnnouncementForm, ActivityForm
from ..models import Login, ExtensionProgram, Beneficiary, Project, Program, Student, Announcement, Registration, Activity
from app import db
from flask_login import current_user, login_user, login_required, logout_user
import string

admin_bp = Blueprint('admin', __name__, template_folder="templates", static_folder="static", static_url_path='static')

@admin_bp.route('/', methods=['GET', 'POST'])
def adminLogin():
    form = LoginForm()
    
    # Prevents logged in users from accessing the page
    if current_user.is_authenticated:
        return redirect(url_for('admin.programs'))  # Temp route

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

@admin_bp.route('/home')
@login_required
def home():
    pass

@admin_bp.route('/programs')
@login_required
def programs():
    form = ProgramForm()
    project_form = ProjectForm()
    programs = ExtensionProgram.query.all()
    projects = Project.query.all()
    
    return render_template('admin/program_management.html', programs=programs, projects=projects, form=form, project_form=project_form)


@admin_bp.route('/extension-program/insert', methods=['POST'])
@login_required
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


@admin_bp.route('/update/extension-program/<int:id>', methods=['POST'])
@login_required
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


@admin_bp.route('/delete/extension-program/<int:id>', methods=['POST'])
@login_required
def deleteExtensionProgram(id):
    extension_program = ExtensionProgram.query.get_or_404(id)
    try:
        db.session.delete(extension_program)
        db.session.commit()
        flash('Extension program is successfully deleted.', category='success')
    except:
        flash('There was an issue deleting the extension program.', category='error')

    return redirect(url_for('admin.programs'))


@admin_bp.route('/extension-program/project/insert', methods=['POST'])
@login_required
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


@admin_bp.route('/extension-program/project/<int:id>', methods=['GET', 'POST'])
@login_required
def viewProject(id):
    form = ProjectForm()
    activity_form = ActivityForm()
    project = Project.query.get_or_404(id)
    registered = Registration.query.filter_by(ProjectId=project.ProjectId)
    # for calendar - temp
    events = fetch_activities(id)
    if request.method == "POST":
        if form.validate_on_submit():
            project.Name = form.project_name.data
            project.LeadProponent= form.lead_proponent.data
            project.ProjectType = form.project_type.data
            project.Rationale = form.rationale.data
            project.Objectives = form.objectives.data
            project.StartDate = form.start_date.data
            project.NumberOfBeneficiaries = form.num_of_beneficiaries.data
            project.BeneficiariesClassifications = form.beneficiaries_classifications.data
            project.ProjectScope = form.project_scope.data

            try:
                db.session.commit()
                flash('Extension project is successfully updated.', category='success')
                return redirect(url_for('admin.viewProject', id=project.ProjectId))
            except:
                flash('There was an issue updating the extension project.', category='error')

        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg)

        return redirect(url_for('admin.viewProject', id=project.ProjectId))
    
    form.lead_proponent.data = project.LeadProponent
    form.project_type.data = project.ProjectType
    form.project_name.data = project.Name
    form.rationale.data = project.Rationale
    form.objectives.data = project.Objectives
    form.start_date.data = project.StartDate
    form.num_of_beneficiaries.data = project.NumberOfBeneficiaries
    form.beneficiaries_classifications.data = project.BeneficiariesClassifications
    form.project_scope.data = project.ProjectScope
    form.extension_program.data = project.ExtensionProgramId

    return render_template('admin/view_project.html', project=project, form=form, activity_form=activity_form, registered=registered, events=events)


@admin_bp.route('/update/extension-program/project/<int:id>', methods=['POST'])
@login_required
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
            flash('Extension project is successfully updated.', category='success')
        except:
            flash('There was an issue updating the extension project.', category='error')

        return redirect(url_for('admin.programs'))
    
    if form.errors != {}: # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(err_msg)

    return redirect(url_for('admin.programs'))


@admin_bp.route('/delete/extension-program/project/<int:id>', methods=['POST'])
@login_required
def deleteProject(id):
    project = Project.query.get_or_404(id)
    try:
        db.session.delete(project)
        db.session.commit()
        flash('Extension project is successfully deleted.', category='success')
    except Exception as e:
        flash('There was an issue deleting the extension project.', category='error')

    return redirect(url_for('admin.programs'))



@admin_bp.route('<int:id>/activity/create', methods=['POST'])
@login_required
def insertActivity(id):
    activity_form = ActivityForm()
    if activity_form.validate_on_submit():
        activity_to_create = Activity(ActivityName=activity_form.name.data,
                                        Date=activity_form.date.data,
                                        StartTime=activity_form.start_time.data,
                                        EndTime=activity_form.end_time.data,
                                        Description=activity_form.description.data,
                                        ProjectId=id)
        db.session.add(activity_to_create)
        db.session.commit()
        flash('Activity is successfully inserted.', category='success')
        return redirect(url_for('admin.viewProject', id=id))
    if activity_form.errors != {}: # If there are errors from the validations
        for err_msg in activity_form.errors.values():
            flash(err_msg, category='error')
    return redirect(url_for('admin.viewProject', id=id))


@admin_bp.route('/beneficiaries')
@login_required
def beneficiaries():
    users = Beneficiary.query.all()
    current_url_path = request.path
    return render_template('admin/users.html', users=users,current_url_path=current_url_path)


@admin_bp.route('/students')
@login_required
def students():
    users = Student.query.all()
    current_url_path = request.path
    return render_template('admin/users.html', users=users,current_url_path=current_url_path)


@admin_bp.route('/calendar')
@login_required
def calendar():
    projects = Project.query.all()
    selected_project_id = request.args.get('project_id', None)
    # Call a function to fetch activities based on the selected project
    activities = fetch_activities(selected_project_id)
    
    return render_template('admin/activity_calendar.html', projects=projects, events=activities, selected_project_id=selected_project_id)


@admin_bp.route('/announcement/<string:project>')
@admin_bp.route('/announcement', defaults={'project': None})
@login_required
def announcement(project):
    bool_is_published_empty = True
    bool_is_draft_empty = True
    if project is not None:
        announcements = Announcement.query.join(Project).filter(Project.Name == project).all()
        for announcement in announcements:
            if announcement.IsLive == 1:
                bool_is_published_empty = False
                break
        for announcement in announcements:
            if announcement.IsLive == 0:
                bool_is_draft_empty = False
                break
    else:
        announcements = Announcement.query.all()
        for announcement in announcements:
            if announcement.IsLive == 1:
                bool_is_published_empty = False
                break
        for announcement in announcements:
            if announcement.IsLive == 0:
                bool_is_draft_empty = False
                break
    programs = Program.query.all()
    return render_template('admin/announcement.html', programs=programs, announcements=announcements, bool_is_published_empty=bool_is_published_empty, bool_is_draft_empty=bool_is_draft_empty)


@admin_bp.route('/announcement/create', methods=['GET', 'POST'])
@login_required
def createAnnouncement():
    form = AnnouncementForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if 'publish' in request.form:
                if not all(request.form.values()):
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
            flash('Announcement is successfully inserted.', category='success')
            return redirect(url_for('admin.announcement'))
        if form.errors != {}: # If there are errors from the validations
            for err_msg in form.errors.values():
                flash(err_msg, category='error')

    return render_template('admin/create_announcement.html', form=form)


@admin_bp.route('/announcement/update/<int:id>', methods=['GET', 'POST'])
@login_required
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


@admin_bp.route('/delete/announcement/<int:id>', methods=['POST'])
@login_required
def deleteAnnouncement(id):
    announcement = Announcement.query.get_or_404(id)
    try:
        db.session.delete(announcement)
        db.session.commit()
        flash('Announcement is successfully deleted.', category='success')
    except:
        flash('There was an issue deleting the announcement.', category='error')

    return redirect(url_for('admin.announcement'))


@admin_bp.route('/unpublish/announcement/<int:id>', methods=['POST'])
@login_required
def unpublishAnnouncement(id):
    announcement = Announcement.query.get_or_404(id)
    announcement.IsLive = 0
    try:
        db.session.commit()
        flash('Announcement is successfully unpublished.', category='success')
    except:
        flash('There was an issue unpublishing the announcement.', category='error')

    return redirect(url_for('admin.announcement'))


@admin_bp.route('/view/announcement/<int:id>/<string:slug>')
@login_required
def viewAnnouncement(id, slug):
    announcement = Announcement.query.filter_by(AnnouncementId=id, Slug=slug).first_or_404()
    return render_template('admin/view_announcement.html', announcement=announcement)


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
