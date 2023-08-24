from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, TextAreaField
from wtforms.validators import Length, Email, DataRequired, Optional

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField(label='Sign in')


class addProjectForm(FlaskForm):
    program_name = StringField(label='Program Name', validators=[DataRequired()])
    target_participant = StringField(label='Target Participant', validators=[DataRequired()])
    location = StringField(label='Location', validators=[DataRequired()])
    status = StringField(label="Status", validators=[DataRequired()])
    start_date = DateField(label='Start Date', validators=[Optional()])
    end_date = DateField(label='End Date', validators=[Optional()])
    description = TextAreaField(label='Description', validators=[DataRequired()])
    objectives = TextAreaField(label='Objectives', validators=[DataRequired()])
    expected_outcome = TextAreaField(label='Expected Outcome', validators=[DataRequired()])
    terms_conditions = TextAreaField(label='Terms and Conditions', validators=[DataRequired()])
    submit = SubmitField(label='Save Project')
