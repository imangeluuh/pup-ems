from app.admin import bp
from flask import render_template, url_for, request, redirect, flash, session
from flask_login import current_user, login_user, login_required, logout_user
from .forms import LoginForm, AnnouncementForm
from ..models import Login, Beneficiary, Project, Program, Student, Announcement, Registration, User
from ..Api.resources import AdminLoginApi
from ..decorators.decorators import login_required
from app import db, api
from ..store import uploadImage
from ..email import sendEmail
from werkzeug.utils import secure_filename
import string, requests
from ..programs.programs import fetch_activities


def saveImage(image, imagepath):
    imagename = secure_filename(image.filename)
    image.save(imagepath)
    # Upload image to imagekit
    return uploadImage(imagepath, imagename)

@bp.route('/', methods=['GET', 'POST'])
def adminLogin():
    form = LoginForm()
    
    # Prevents logged in users from accessing the page
    if current_user.is_authenticated:
        return redirect(url_for('programs.programs'))  # Temp route
    
    if request.method == "POST":
        if form.validate_on_submit():
            data={'Email': form.email.data,
                'Password': form.password.data}
            response = requests.post(api.url_for(AdminLoginApi, _external=True), json=data)
            if response.status_code == 200:
                response_data = response.json()
                session['access_token'] = response_data.get('access_token')
                instance_user = Login()
                instance_user.set_user_data(login_data=response_data['admin'])
                login_user(instance_user, remember=True)
                return redirect(url_for('programs.programs')) # Temp route
            else:
                response_data = response.json()
                flash(response_data.get('error'), category='error')
    return render_template('admin/admin_login.html', form=form)

@bp.route('/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('admin.adminLogin'))

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

@bp.route('/extension-program')
@login_required(role=["Admin"])
def extensionProgram():
    program_abbreviation = request.args.get('program')
    program = Program.query.filter_by(Abbreviation=program_abbreviation).first()
    print(program.ExtensionPrograms)
    ext_programs = [ext_program for ext_program in program.ExtensionPrograms]
    return render_template('admin/ext_program_options.html', ext_programs=ext_programs)


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
@login_required(role=["Admin", "Faculty"])
def createAnnouncement():
    form = AnnouncementForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if 'publish' in request.form:
                if not all(request.form.values()):
                    # Save the input to session
                    session['announcement_title']= form.title.data
                    session['announcement_body'] = form.content.data
                    flash('Please fill out all the fields before publishing.', category='error')
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
                    flash('Please fill out all the fields before publishing.', category='error')
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
    return render_template('admin/view_user.html', user=user, user_projects=user_projects)


def generateSlug(title, separator='-', lower=True):
    title = title.translate(str.maketrans('', '', string.punctuation))
    if lower:
        title = title.lower()
    return separator.join(title.split())