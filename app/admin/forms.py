from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, TextAreaField, IntegerField, HiddenField
from wtforms.validators import Length, Email, DataRequired, Optional
from ..models import Agenda, Program, Project
from flask_ckeditor import CKEditorField

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField(label='Sign in')


class ProgramForm(FlaskForm):
    program_name = StringField(label='Extension Program Name', validators=[DataRequired()])
    agenda = SelectField(label='Agenda', validators=[DataRequired()])
    program = SelectField(label='Program', validators=[DataRequired()])
    date_approved = DateField(label='Date Approved', validators=[Optional()])
    implementation_date = DateField(label='Implementation Date', validators=[Optional()])
    status = StringField(label='Status', validators=[DataRequired()])
    submit = SubmitField(label='Save Program')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        with current_app.app_context():
            self.agenda.choices = [(agenda.AgendaId, agenda.AgendaName) for agenda in Agenda.query.all()]
            self.program.choices = [(program.ProgramId, program.ProgramName) for program in Program.query.all()]


class ProjectForm(FlaskForm):
    project_name = StringField(label="Project Name", validators=[DataRequired()])
    lead_proponent = StringField(label="Lead Proponent", validators=[DataRequired()])
    project_type = SelectField(label="Project Type", choices=[('Need-Based', 'Need-Based'),
                                                            ('Quick Response', 'Quick Response'),
                                                            ('Other Related Activities/Collaboration', 'Other Related Activities/Collaboration')],
                                                            validators=[DataRequired()])
    rationale = TextAreaField(label="Rationale / Description of the Project", validators=[DataRequired()])
    objectives = TextAreaField(label="Objective of the Project", validators=[DataRequired()])
    start_date = DateField(label="Start Date", validators=[Optional()])
    num_of_beneficiaries = IntegerField(label="Specific Numbers of Target Beneficiaries", validators=[Optional()])
    beneficiaries_classifications = StringField(label="Target Beneficiaries Classifications", validators=[Optional()])
    project_scope = TextAreaField(label="Scope of Project", validators=[DataRequired()])
    extension_program = HiddenField(validators=[DataRequired()])
    submit = SubmitField(label="Save Project") 


class AnnouncementForm(FlaskForm):
    title = StringField(label="Announcement Title")
    content = CKEditorField(label="Announcement Content")
    project = SelectField(label='Extension Project')
    publish = SubmitField(label="Publish") 
    draft = SubmitField(label="Save as Draft") 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        with current_app.app_context():
            self.project.choices = [(project.ProjectId, project.Name) for project in Project.query.all()]
