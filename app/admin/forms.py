from flask import current_app
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, TextAreaField, IntegerField, HiddenField, TimeField, SelectMultipleField, widgets
from wtforms.validators import Length, Email, DataRequired, Optional
from flask_wtf.file import FileField, FileAllowed
from ..models import Agenda, Program, Project

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign in')


class ProgramForm(FlaskForm):
    program_name = StringField('Extension Program Name', validators=[DataRequired()])
    agenda = SelectField('Agenda', validators=[DataRequired()])
    image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    program = SelectField('Program', validators=[DataRequired()])
    date_approved = DateField('Date Approved', validators=[Optional()])
    implementation_date = DateField('Implementation Date', validators=[Optional()])
    status = StringField('Status', validators=[DataRequired()])
    submit = SubmitField('Save Program')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        with current_app.app_context():
            self.agenda.choices = [(agenda.AgendaId, agenda.AgendaName) for agenda in Agenda.query.all()]
            self.program.choices = [(program.ProgramId, program.ProgramName) for program in Program.query.all()]


class ProjectForm(FlaskForm):
    project_name = StringField("Project Name", validators=[DataRequired()])
    lead_proponent = StringField("Lead Proponent", validators=[DataRequired()])
    status = StringField('Status', validators=[DataRequired()])
    project_type = SelectField("Project Type", choices=[('Need-Based', 'Need-Based'),
                                                            ('Quick Response', 'Quick Response'),
                                                            ('Other Related Activities/Collaboration', 'Other Related Activities/Collaboration')],
                                                            validators=[DataRequired()])
    rationale = TextAreaField("Rationale / Description of the Project", validators=[DataRequired()])
    objectives = TextAreaField("Objective of the Project", validators=[DataRequired()])
    image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    start_date = DateField("Start Date", validators=[Optional()])
    num_of_beneficiaries = IntegerField("Specific Numbers of Target Beneficiaries", validators=[Optional()])
    beneficiaries_classifications = StringField("Target Beneficiaries Classifications", validators=[Optional()])
    project_scope = TextAreaField("Scope of Project", validators=[DataRequired()])
    extension_program = HiddenField()
    submit = SubmitField("Save Project") 


class AnnouncementForm(FlaskForm):
    title = StringField("Announcement Title")
    content = CKEditorField("Announcement Content")
    project = SelectField('Extension Project')
    publish = SubmitField("Publish") 
    draft = SubmitField("Save as Draft") 
    medium = MultiCheckboxField("Medium", choices=[('Bulletin', 'Bulletin'), ('Email', 'Email')])
    recipient = MultiCheckboxField("Recipient", choices=[('2', 'Beneficiaries'), ('3', 'Students')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        with current_app.app_context():
            self.project.choices = [(project.ProjectId, project.Name) for project in Project.query.all()]


class ActivityForm(FlaskForm):
    name = StringField("Activity Name", validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()])
    start_time = TimeField("Start Time", format='%H:%M', validators=[DataRequired()])
    end_time = TimeField('End Time', format='%H:%M', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    project = HiddenField()
    save = SubmitField("Save Activity") 
