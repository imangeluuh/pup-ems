from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, TextAreaField, IntegerField, HiddenField, TimeField, FormField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileField, FileAllowed
from ..models import Agenda, Program, Collaborator, Speaker

class ProgramForm(FlaskForm):
    program_name = StringField('Extension Program Name', validators=[DataRequired()])
    agenda = SelectField('Agenda', validators=[DataRequired()])
    collaborator = SelectField('Collaborator', validators=[DataRequired()])
    proposed_budget = StringField('Proposed Budget', validators=[DataRequired()])
    approved_budget = StringField('Approved Budget', validators=[DataRequired()])
    fund_type = SelectField('Fund Type', choices=[('Internal', 'Internal'),
                                                ('External', 'External')],
                                                validators=[DataRequired()])
    image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    program = SelectField('Program', validators=[DataRequired()])
    date_approved = DateField('Date Approved', validators=[DataRequired()])
    implementation_date = DateField('Implementation Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[('To be started', 'To be started'),
                                            ('Ongoing', 'Ongoing'),
                                            ('Finished', 'Finished')],
                                            validators=[DataRequired()])
    submit= SubmitField('Save Program')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        with current_app.app_context():
            self.agenda.choices = [(agenda.AgendaId, agenda.AgendaName) for agenda in Agenda.query.all()]
            self.program.choices = [(program.ProgramId, program.ProgramName) for program in Program.query.all()]
            self.collaborator.choices = [(collaborator.CollaboratorId, collaborator.Organization) for collaborator in Collaborator.query.all()]

class ProjectForm(FlaskForm):
    project_name = StringField("Project Name", validators=[DataRequired()])
    status = SelectField('Status', choices=[('To be started', 'To be started'),
                                        ('Ongoing', 'Ongoing'),
                                        ('Finished', 'Finished')],
                                        validators=[DataRequired()])
    project_type = SelectField("Project Type", choices=[('Need-Based', 'Need-Based'),
                                                            ('Quick Response', 'Quick Response'),
                                                            ('Other Related Activities/Collaboration', 'Other Related Activities/Collaboration')],
                                                            validators=[DataRequired()])
    rationale = TextAreaField("Rationale / Description of the Project", validators=[DataRequired()])
    objectives = TextAreaField("Objective of the Project", validators=[DataRequired()])
    image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    start_date = DateField("Start Date", validators=[DataRequired()])
    num_of_beneficiaries = IntegerField("Specific Numbers of Target Beneficiaries", validators=[Optional()])
    beneficiaries_classifications = StringField("Target Beneficiaries Classifications", validators=[Optional()])
    project_scope = TextAreaField("Scope of Project", validators=[DataRequired()])
    extension_program = HiddenField()
    submit = SubmitField("Save Project") 

class ActivityForm(FlaskForm):
    activity_name = StringField("Activity Name", validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()])
    speaker = SelectField('Speaker', validators=[DataRequired()])
    start_time = TimeField("Start Time", format='%H:%M', validators=[DataRequired()])
    end_time = TimeField('End Time', format='%H:%M', validators=[DataRequired()])
    activity_description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    project = HiddenField()
    save = SubmitField("Save Activity") 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        with current_app.app_context():
            self.speaker.choices = [(speaker.SpeakerId, speaker.FirstName + " " + speaker.LastName) for speaker in Speaker.query.all()]

class CombinedForm(FlaskForm):
    extension_program = FormField(ProgramForm)
    project = FormField(ProjectForm)
    activity = FormField(ActivityForm)
    submit = SubmitField("Submit") 