from app.programs import bp
from flask import render_template, url_for, request, redirect, flash, current_app
from flask_login import current_user
from ..models import Project, ExtensionProgram, Program, Registration, Agenda, ExtensionProgram, Activity, Question, Survey, Response, Beneficiary, Attendance, User, Certificate
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
                                        SpeakerId=form.activity.speaker.data,
                                        Description=form.activity.activity_description.data,
                                        ProjectId=int_project_id,
                                        ImageUrl=str_image_url,
                                        ImageFileId=str_image_file_id)
        db.session.add(activity_to_create)
        db.session.commit()
        flash('Extension program is successfully inserted.', category='success')
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
                
        activity_to_create = Activity(ActivityName=form.activity_name.data,
                                        Date=form.date.data,
                                        StartTime=form.start_time.data,
                                        EndTime=form.end_time.data,
                                        SpeakerId=form.speaker.data,
                                        Description=form.activity_description.data,
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
        activity.ActivityName=form.activity_name.data
        activity.Date=form.date.data
        activity.Description=form.activity_description.data
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
        print(e)
        flash('There was an issue deleting the activity', category='error')

    return redirect(url_for('programs.viewProject', id=project_id))

@bp.route('/budget-allocation')
@login_required(role=["Admin", "Faculty"])
def budgetAllocation():
    ext_programs = ExtensionProgram.query.all()
    return render_template('admin/budget_allocation.html', ext_programs=ext_programs)

@bp.route('/questions')
@login_required(role=["Admin", "Faculty"])
def questions():
    mandatory_questions = Question.query.filter_by(State = 1, Required = 1).all()
    optional_questions = Question.query.filter_by(State = 1, Required = 0).all()

    return render_template('admin/questions.html', mandatory_questions=mandatory_questions, optional_questions=optional_questions)

#delete question - deletest question from pool and redirects back to questions
@bp.route("/questions/delete/<id>")
@login_required(role=["Admin", "Faculty"])
def deleteQuestion(id):

    question = Question.query.filter_by(QuestionId=id).first()

    if question:
        question.State = 0
        db.session.commit()

    flash('The question has been deleted successfully.', category='success')
    return redirect(url_for("programs.questions"))


@bp.route('/questions/add', methods=['GET', 'POST'])
@login_required(role=["Admin", "Faculty"])
def addQuestions():
    if request.method == "POST":
        question_text = request.form["question"]
        responses = list(filter(None, request.form.getlist("responses")))
        question_type = 1
        if request.form["type"] == 'Text':
            question_type = 2
            responses = []
        required = 1
        if request.form['optional'] == '1':
            required = 0

        if question_text.isspace() or question_text == "" or question_type == 1 and (len(responses) < 2 or all(responses[i].isspace() for i in range(0, len(responses)-1))):
            flash('Please complete all required fields.', category='error')
            return render_template("admin/add_question.html")
        
        if not question_type in range(1,3):
            flash('The application could not complete your request at this moment. Please try again later.', category='error')
            return render_template("admin/add_question.html")
        
        try:
            question_to_add = Question(Text=question_text, State=1, Type=question_type, Required=required, Responses=str(responses))
            db.session.add(question_to_add)
            db.session.commit()
            flash('Your question has been successfully added to the pool.', category='success')
        except:
            flash('An error occured whilst adding your question to the pool. Please try again later.', category='error')
    return render_template("admin/add_question.html")


@bp.route('/surveys')
@login_required(role=["Admin", "Faculty"])
def surveys():
    active_surveys = None
    inactive_surveys = None

    if current_user.Role.RoleId == 1:
        active_surveys = Survey.query.filter_by(State = 1).all()
        inactive_surveys = Survey.query.filter_by(State = 0).all()
    else:
        list_activities = [r.Project.Activity for r in Registration.query.filter_by(UserId=current_user.User[0].UserId).all()]
        # Initialize an empty list to store the ActivityIds
        list_activity_ids = []
        
        # Iterate through the outer list
        for sublist in list_activities:
            # Iterate through the inner list
            for activity in sublist:
                list_activity_ids.append(activity.ActivityId)  
        
        active_surveys = Survey.query.filter(Survey.ActivityId.in_(list_activity_ids)).filter_by(State = 1).all()
        inactive_surveys = Survey.query.filter(Survey.ActivityId.in_(list_activity_ids)).filter_by(State = 0).all()

    return render_template("admin/surveys.html", active_surveys=active_surveys, inactive_surveys=inactive_surveys)


@bp.route('/surveys/add', methods=['GET', 'POST'])
@login_required(role=["Admin", "Faculty"])
def addSurvey():
    questions = Question.query.filter_by(State = 1).all()
    activities = Activity.query.all()
    if request.method == "POST":

        survey_name = request.form["name"]
        survey_activity = request.form["activity"]
        survey_questions = request.form.getlist("questions")

        if survey_name.isspace() or survey_name == "" or not survey_questions or not survey_activity:
            flash('Please complete all required fields.', category='error')

        try:
            survey_to_add = Survey(SurveyName=survey_name, ActivityId=survey_activity, State=2, Questions=str(survey_questions))
            db.session.add(survey_to_add)
            db.session.commit()
            flash('Survey is successfully created.', category='success')
        except:
            flash('An error occured whilst creating your survey. Please try again later.', category='error')

    return render_template('admin/add_survey.html', questions=questions, activities=activities)

#close survey - makes survey inactive and redirects to surveys page
@bp.route("/surveys/close/<id>")
@login_required(role=["Admin", "Faculty"])
def closeSurvey(id):
    survey = Survey.query.filter_by(SurveyId=id).first()

    try:
        if survey:
            survey.State = 0
            db.session.commit()
            flash('The survey has been closed successfully.')
    except:
        flash('The survey could not be closed. Please try again later.')

    return redirect(url_for("programs.surveys"))

#results page - show survey results
@bp.route("/results/<id>")
@login_required(["Admin", "Faculty"])
def results(id):

    list_activities = [r.Project.Activity for r in Registration.query.filter_by(UserId=current_user.User[0].UserId).all()]
    # Initialize an empty list to store the ActivityIds
    list_activity_ids = []
    
    # Iterate through the outer list
    for sublist in list_activities:
        # Iterate through the inner list
        for activity in sublist:
            list_activity_ids.append(activity.ActivityId) 

    survey = Survey.query.filter_by(SurveyId=id).first()

    if not survey: 
        flash('The survey you have requested does not exist. Please check your link is correct.', category='error')
        return render_template("admin/results.html")

    questions = []
    for question_id in survey.questionsList():
        question = Question.query.filter_by(QuestionId=question_id).first()
        questions.append(question)

    responses = Response.query.filter_by(SurveyId=id).all()

    return render_template("admin/results.html", survey=survey, questions=questions, responses=responses)

from fillpdf import fillpdfs

@bp.route('/cert/<int:id>', methods=['GET', 'POST'])
@login_required(role=["Admin", "Faculty"])
def cert(id):
    fillpdfs.get_form_fields("C:\\Users\\angel\\Desktop\\e-cert (beneficiary) (FILLABLE).pdf")
    fillpdfs.print_form_fields("C:\\Users\\angel\\Desktop\\e-cert (beneficiary) (FILLABLE).pdf")
    
    # Get all the registered beneficiaries in the project
    beneficiaries_id = [registration.UserId for registration in Registration.query.filter_by(ProjectId=id).all()]
    registered_beneficiaries = [User.query.filter_by(UserId=beneficiary_id).first() for beneficiary_id in beneficiaries_id]
    
    # Get the project proponent's name for the certificate
    project = Project.query.filter_by(ProjectId=id).first()
    project_proponent = User.query.filter_by(UserId=project.LeadProponentId).first()
    proponent_name = project_proponent.FirstName + ' '
    if project_proponent.MiddleName:
        proponent_name += project_proponent.MiddleName[0] + '. '
    proponent_name += project_proponent.LastName

    # Get the extension program's name for the certificate
    extension_program = ExtensionProgram.query.filter_by(ExtensionProgramId=project.ExtensionProgramId).first()
    
    # Generate certificate for each beneficiary registered in the project
    for beneficiary in registered_beneficiaries:
        # Get the name of the beneficiary for the certificate
        beneficiary_name = beneficiary.FirstName + ' '
        if beneficiary.MiddleName:
            beneficiary_name += beneficiary.MiddleName[0] + '. '
        beneficiary_name += beneficiary.LastName
        print(beneficiary_name)
        data_dict = {'Text-n_L-ntAGRy': beneficiary_name,
                    'Text-Pnb29VfGWk': extension_program.Name,
                    'Date-jWSJ8ZAYJ_': datetime.utcnow(),
                    'Text-tf2etyjp87': proponent_name,
                    'Text-bcixq7yk8z': 'Jaime P. Gutierrez, Jr.'}
        
        # Get the initials of the beneficiary
        beneficiary_initials = ''.join([word[0] for word in beneficiary_name.split()])
        # Fill the pdf with the required information
        filepath = os.path.join(current_app.root_path, "media") + "\\" + extension_program.Name + "-" + beneficiary_initials + " CERTIFICATE.pdf"
        fillpdfs.write_fillable_pdf("C:\\Users\\angel\\Desktop\\e-cert (beneficiary) (FILLABLE).pdf", filepath, data_dict, flatten=True)

        # Upload cert pdf to cloud
        status = uploadImage(filepath, extension_program.Name + "-" + beneficiary_initials + " CERTIFICATE.pdf")

        # Get the url and file id of the uploaded certificate
        str_cert_url = None
        str_cert_file_id = None
        if status.error is not None:
            flash("Error in releasing certificates", category="error")
            return url_for('programs.viewProject', id=id)
        else:
            str_cert_url = status.url
            str_cert_file_id = status.file_id

        # Delete file from local storage after uploading to cloud
        if os.path.exists(filepath):
            os.remove(filepath)

        # Save certificate to database
        cert_to_add = Certificate(CertificateUrl=str_cert_url, 
                                CertificateFileId = str_cert_file_id, 
                                UserId=beneficiary.UserId, 
                                ProjectId=id)
        
        db.session.add(cert_to_add)
    
    db.session.commit()

    return redirect(url_for('programs.programs'))


# =========================================================
# ||                      USER VIEWS                     ||
# =========================================================

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
    current_date = datetime.utcnow()
    list_activities = project.Activity
    user_id = current_user.User[0].UserId if current_user.is_authenticated else None
    bool_is_registered = True if Registration.query.filter_by(ProjectId=project_id, UserId=user_id).first() else False
    if request.method == 'POST':
        registration_to_create = Registration(ProjectId = project_id,
                                            UserId=user_id)
        try:
            db.session.add(registration_to_create)
            db.session.commit()
            flash('Registration Successful!', category='success')
        except:
            flash('There was an issue during registration.', category='error')

        return redirect(url_for('programs.registration', project_id=project_id))
    return render_template("programs/project_reg.html", project=project, list_activities=list_activities, bool_is_registered=bool_is_registered, current_date=current_date)


@bp.route('/registration/cancel/<int:project_id>', methods=['POST'])
def cancelRegistration(project_id):
    project = Project.query.get_or_404(project_id)
    user_id = current_user.User[0].UserId if current_user.is_authenticated else None
    registration = Registration.query.filter_by(ProjectId=project_id, UserId=user_id).first()

    try:
        db.session.delete(registration)
        db.session.commit()
        flash('Registration is successfully canceled.', category='success')
    except:
        flash('There was an issue canceling the registration.', category='error')

    return redirect(url_for('programs.registration', project_id=project_id))


#survey page - allows responses to be collected
@bp.route("/survey/<id>", methods=["GET", "POST"])
@login_required(role=["Beneficiary"])
def survey(id):
    
    #check whether student is enrolled in course and hasn't already taken survey
    list_activities = [r.Project.Activity for r in Registration.query.filter_by(UserId=current_user.User[0].UserId).all()]
    # Initialize an empty list to store the ActivityIds
    list_activity_ids = []
    
    # Iterate through the outer list
    for sublist in list_activities:
        # Iterate through the inner list
        for activity in sublist:
            list_activity_ids.append(activity.ActivityId)  

    survey = Survey.query.filter_by(SurveyId=id).first()
    if survey.ActivityId not in list_activity_ids:
        return redirect(url_for('programs.surveys'))

    if not survey: 
        flash('The survey you have requested does not exist. Please check your link is correct.', category='error')
        return render_template("admin/survey.html")
    
    if Response.query.filter_by(SurveyId=id, BeneficiaryId=current_user.User[0].UserId).first():
        survey_taken = True
        return render_template("admin/survey.html", survey=survey, survey_taken=survey_taken)

    questions = []
    for question_id in survey.questionsList():
        question = Question.query.filter_by(QuestionId=question_id).first()
        questions.append(question)

    if request.method == "POST":
        error = 0

        #check for required fields
        for question in questions:
            response = request.form.get(str(question.QuestionId))
            if question.Required and (response == None or response.isspace() or response == ""):
                flash('Please fill out all the required fields', category='error')
                return render_template("admin/survey.html", survey=survey, questions=questions)

        #submit responses
        for question in questions:
            response = request.form.get(str(question.QuestionId))

            if not response is None and not response.isspace() and response != "":
                if question.Type == 1:
                    if not save_response(id, current_user.User[0].UserId, question.QuestionId, None, int(response)):
                        error = 1
                        break

                elif question.Type == 2:
                    if not save_response(id, current_user.User[0].UserId, question.QuestionId, response, None):
                        error = 1
                        break
        if not error:
            attendance = Attendance(HasAttended = True, BeneficiaryId=current_user.User[0].UserId, ActivityId = survey.ActivityId)
            db.session.add(attendance)
            db.session.commit()
            flash('Your response has been recorded successfully. Survey results will be made available to you through your dashboard when the survey closes.', category='success')
            return redirect(url_for('programs.survey', id=id))
        else:
            flash('An error occured whilst recording your response. Please try again later.', category='error')
        
    return render_template("admin/survey.html", survey=survey, questions=questions)

def save_response(survey_id, user_id, question_id, text, num):
    if (text is None and num is None):
        return 0 #failure
    if not Survey.query.filter_by(SurveyId=survey_id).first():
        return 0 #failure: invalid survey id
    if not Beneficiary.query.filter_by(BeneficiaryId=user_id).first():
        return 0 #failure: invalid user id
    if not Question.query.filter_by(QuestionId=question_id).first():
        return 0 #failure: invalid question id

    response_to_add = Response(SurveyId=survey_id, BeneficiaryId=user_id, QuestionId=question_id, Text=text, Num=num)
    db.session.add(response_to_add)
    db.session.commit()
    return 1

# Define a new function to fetch activities based on the selected project
def fetch_activities(selected_project_id=None):

    query = Activity.query

    if selected_project_id:
        query = query.filter(Activity.ProjectId == selected_project_id)

    return query.with_entities(Activity.ActivityName, Activity.Date, Project.Name).join(Project).all()