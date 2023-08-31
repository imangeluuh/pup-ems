from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, TextAreaField
from wtforms.validators import Length, Email, DataRequired, Optional

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField(label='Sign in')


class ProjectForm(FlaskForm):
    program_name = StringField(label='Extension Program Name', validators=[DataRequired()])
    agenda = StringField(label='Agenda', validators=[DataRequired()])
    program = StringField(label='Program', validators=[DataRequired()])
    date_approved = DateField(label='Date Approved', validators=[Optional()])
    implementation_date = DateField(label='Implementation Date', validators=[Optional()])
    status = StringField(label="Status", validators=[DataRequired()])
    submit = SubmitField(label='Save Program')
