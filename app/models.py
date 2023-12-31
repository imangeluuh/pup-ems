from flask import url_for
from app import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
from time import time
from flask_jwt_extended import create_access_token, decode_token
import ast

@login_manager.user_loader
def load_user(user_id):
    return Login.query.get(user_id)

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page=page, per_page=per_page, error_out=False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page, **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page, **kwargs) if resources.has_prev else None,
            }
        }
        return data


class Role(db.Model):
    __tablename__ = 'Role'

    RoleId = db.Column(db.Integer, primary_key=True)
    RoleName = db.Column(db.String(14), nullable=False)
    Login = db.relationship("Login", backref='Role', lazy=True, passive_deletes=True)


class Login(db.Model, UserMixin):
    __tablename__ = 'Login'

    LoginId = db.Column(db.String(36), primary_key=True)
    Email = db.Column(db.String(100), nullable=False, index=True, unique=True)
    Password = db.Column(db.String(60), nullable=False)
    Status = db.Column(db.String(20), default='Active')
    RoleId = db.Column(db.Integer, db.ForeignKey('Role.RoleId', ondelete='CASCADE'), nullable=False)

    @property
    def password_hash(self):
        return self.password_hash

    @password_hash.setter
    def password_hash(self, plain_text_password):
        self.Password = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.Password, attempted_password)
    
    def get_reset_password_token(self, expires_in=10):
        return create_access_token(identity={'reset_password': self.LoginId},expires_delta=timedelta(minutes=expires_in))

    @staticmethod
    def verify_reset_password_token(token):
        try:
            decoded_token = decode_token(token)
            login_id= decoded_token['sub']['reset_password']
        except:
            return
        return Login.query.get(login_id)

    def get_id(self):
        return self.LoginId

    def get_role(self):
        return(self.Role.RoleName)
    
    def set_user_data(self, login_data):
        self.LoginId = login_data['LoginId']
        self.Email = login_data['Email']
        self.Password = login_data['Password']
        self.Status = login_data['Status']
        self.RoleId = login_data['RoleId']

    def to_dict(self):
        data = {
            'LoginId': self.LoginId,
            'Email': self.Email,
            'Password': self.Password,
            'Status': self.Status,
            'RoleId': self.RoleId,
        }
        return data


class User(PaginatedAPIMixin, db.Model):
    __tablename__ = 'User'

    UserId = db.Column(db.String(36), primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    MiddleName = db.Column(db.String(50), default=None)
    LastName = db.Column(db.String(50), nullable=False)
    ContactDetails = db.Column(db.String(13), nullable=False)
    Birthdate = db.Column(db.Date, nullable=False)
    Gender = db.Column(db.String(20), nullable=False)
    Address = db.Column(db.String(255), nullable=False)
    LoginId = db.Column(db.String(36), db.ForeignKey('Login.LoginId', ondelete='CASCADE'), nullable=False)
    Registration = db.relationship('Registration', backref='User', cascade='all, delete-orphan', passive_deletes=True)
    Login = db.relationship("Login", backref='User', lazy=True, passive_deletes=True)
    Certificate = db.relationship("Certificate", back_populates="User")

class Admin(db.Model):
    __tablename__ = 'Admin'

    AdminId = db.Column(db.String(36), db.ForeignKey('User.UserId', ondelete='CASCADE'), primary_key=True)
    User = db.relationship("User", backref='Admin', lazy=True, passive_deletes=True)


class Faculty(db.Model):
    __tablename__ = 'Faculty'

    FacultyId = db.Column(db.String(36), db.ForeignKey('User.UserId', ondelete='CASCADE'), primary_key=True)
    User = db.relationship("User", backref='Faculty', lazy=True, passive_deletes=True)


class Beneficiary(db.Model):
    __tablename__ = 'Beneficiary'

    BeneficiaryId = db.Column(db.String(36), db.ForeignKey('User.UserId', ondelete='CASCADE'), primary_key=True)
    User = db.relationship("User", backref='Beneficiary', lazy=True, passive_deletes=True)
    SurveyResponse = db.relationship("Response", back_populates="Beneficiary")
    Attendance = db.relationship("Attendance", back_populates="Beneficiary")

class Student(db.Model):
    __tablename__ = 'Student'

    StudentId = db.Column(db.String(36), db.ForeignKey('User.UserId', ondelete='CASCADE'), primary_key=True)
    SkillsInterest = db.Column(db.String(255), nullable=False)
    User = db.relationship("User", backref='Student', lazy=True, passive_deletes=True)


class ExtensionProgram(db.Model):
    __tablename__ = 'ExtensionProgram'

    ExtensionProgramId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    DateApproved = db.Column(db.Date, nullable=False)
    ImplementationDate = db.Column(db.Date)
    Status = db.Column(db.String(20), nullable=False) # move to Project Model
    ImageUrl = db.Column(db.Text)
    ImageFileId = db.Column(db.Text)
    ProposedBudget = db.Column(db.Numeric(12, 2), nullable=False)
    ApprovedBudget = db.Column(db.Numeric(12, 2), nullable=False)
    FundType = db.Column(db.String(20), nullable=False)
    AgendaId = db.Column(db.Integer, db.ForeignKey('Agenda.AgendaId', ondelete='CASCADE'), nullable=False)
    Agenda = db.relationship("Agenda", back_populates='ExtensionPrograms', lazy=True, passive_deletes=True)
    ProgramId = db.Column(db.Integer, db.ForeignKey('Program.ProgramId', ondelete='CASCADE'), nullable=False)
    Program = db.relationship("Program", back_populates='ExtensionPrograms', lazy=True, passive_deletes=True)
    CollaboratorId = db.Column(db.Integer, db.ForeignKey('Collaborator.CollaboratorId', ondelete='CASCADE'), nullable=False)
    Collaborator = db.relationship("Collaborator", back_populates='ExtensionPrograms', lazy=True)
    Projects = db.relationship("Project", back_populates='ExtensionProgram', lazy=True)


class Project(db.Model):
    __tablename__ = 'Project'

    ProjectId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    ProjectType = db.Column(db.String(100), nullable=False)
    Rationale = db.Column(db.String(255), nullable=False)
    Objectives = db.Column(db.String(255), nullable=False)
    Status = db.Column(db.String(20), nullable=False) 
    ImageUrl = db.Column(db.Text)
    ImageFileId = db.Column(db.Text)
    StartDate = db.Column(db.Date)
    LeadProponentId = db.Column(db.String(36), db.ForeignKey('User.UserId', ondelete='CASCADE'), nullable=False)
    NumberOfBeneficiaries = db.Column(db.Integer, nullable=False)
    BeneficiariesClassifications = db.Column(db.String(255), nullable=False)
    ProjectScope = db.Column(db.String(255), nullable=False)
    ExtensionProgramId = db.Column(db.Integer, db.ForeignKey('ExtensionProgram.ExtensionProgramId', ondelete='CASCADE'), nullable=False)
    ExtensionProgram = db.relationship("ExtensionProgram", back_populates='Projects', lazy=True, passive_deletes=True)
    Registration = db.relationship('Registration', backref='Project', cascade='all, delete-orphan', passive_deletes=True)
    LeadProponent = db.relationship('User', backref='Project', lazy=True, passive_deletes=True)
    Certificate = db.relationship('Certificate', back_populates='Project')
    # CommunityAssessment =
    # MOU/MOAAssessment = 


class Program(db.Model):
    __tablename__ = 'Program'

    ProgramId = db.Column(db.Integer, primary_key=True)
    ProgramName = db.Column(db.String(255), nullable=False)
    Abbreviation = db.Column(db.String(255), nullable=False)
    ExtensionPrograms = db.relationship("ExtensionProgram", back_populates='Program', lazy=True)


class Agenda(db.Model):
    __tablename__ = 'Agenda'

    AgendaId = db.Column(db.Integer, primary_key=True)
    AgendaName = db.Column(db.String(255), nullable=False)
    ExtensionPrograms = db.relationship("ExtensionProgram", back_populates='Agenda', lazy=True)


class Collaborator(db.Model):
    __tablename__ = 'Collaborator'

    CollaboratorId = db.Column(db.Integer, primary_key=True)
    Organization = db.Column(db.String(100), nullable=False)
    KeyPersonnel = db.Column(db.String(100), nullable=False)
    Location = db.Column(db.String(255), nullable=False)
    ExtensionPrograms = db.relationship("ExtensionProgram", back_populates='Collaborator', lazy=True)


class Activity(db.Model):
    __tablename__ = 'Activity'

    ActivityId = db.Column(db.Integer, primary_key=True)
    ActivityName = db.Column(db.String(255), nullable=False)
    Date = db.Column(db.Date, index=True, nullable=False)
    StartTime = db.Column(db.Time, nullable=False)
    EndTime = db.Column(db.Time, nullable=False)
    Description = db.Column(db.String(255), nullable=False)
    ImageUrl = db.Column(db.Text)
    ImageFileId = db.Column(db.Text)
    ProjectId = db.Column(db.Integer, db.ForeignKey('Project.ProjectId', ondelete='CASCADE'), nullable=False)
    SpeakerId = db.Column(db.Integer, db.ForeignKey('Speaker.SpeakerId', ondelete='CASCADE'), nullable=False)
    Project = db.relationship('Project', backref='Activity')
    Survey = db.relationship("Survey", back_populates='Activity', cascade='all, delete-orphan', lazy=True)
    Speaker = db.relationship('Speaker', back_populates='Activity')
    Attendance = db.relationship('Attendance', back_populates='Activity', cascade='all, delete-orphan')

class Speaker(db.Model):
    __tablename__ = 'Speaker'

    SpeakerId = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    MiddleName = db.Column(db.String(50), default=None)
    LastName = db.Column(db.String(50), nullable=False)
    ContactDetails = db.Column(db.String(13), nullable=False)
    Activity = db.relationship("Activity", back_populates="Speaker")

class Announcement(db.Model):
    __tablename__ = 'Announcement'

    AnnouncementId = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(255), nullable=False)
    Content= db.Column(db.Text)
    CreatorId = db.Column(db.String(36), db.ForeignKey('User.UserId', ondelete='CASCADE'), nullable=False)
    IsLive = db.Column(db.Boolean, index=True, nullable=False)
    Slug = db.Column(db.String(255), nullable=False)
    Created = db.Column(db.DateTime, default=datetime.utcnow, index=True, nullable=False)
    Updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True, nullable=False)
    ProjectId = db.Column(db.Integer, db.ForeignKey('Project.ProjectId', ondelete='CASCADE'), nullable=False)
    Project = db.relationship('Project', backref='Announcement')
    Creator = db.relationship('User', backref='Announcement')


class Registration(db.Model):
    __tablename__ = 'Registration'

    RegistrationId = db.Column(db.Integer, primary_key=True)
    RegistrationDate = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    ProjectId = db.Column(db.Integer, db.ForeignKey('Project.ProjectId', ondelete='CASCADE'), nullable=False)
    UserId = db.Column(db.String(36), db.ForeignKey('User.UserId', ondelete='CASCADE'), nullable=False)


class Question(db.Model):
    __tablename__ = 'Question'

    QuestionId = db.Column(db.Integer, primary_key=True)
    Text = db.Column(db.Text, nullable=False)
    State = db.Column(db.Integer, nullable=False)
    Type = db.Column(db.Integer, nullable=False)
    Required = db.Column(db.Integer, nullable=False)
    Responses = db.Column(db.Text, nullable=False)
    Response = db.relationship("Response", back_populates="Question")

    def responsesList(self):
        return ast.literal_eval(self.Responses)


class Survey(db.Model):
    __tablename__ = 'Survey'

    SurveyId = db.Column(db.Integer, primary_key=True)
    SurveyName = db.Column(db.Text, nullable=False)
    ActivityId = db.Column(db.Integer, db.ForeignKey('Activity.ActivityId', ondelete='CASCADE'), nullable=False)
    State = db.Column(db.Integer, nullable=False)
    Questions = db.Column(db.Text, nullable=False)
    CreatedAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    Activity = db.relationship("Activity", back_populates="Survey", passive_deletes=True)
    Response = db.relationship("Response", back_populates="Survey", cascade='all, delete-orphan')

    def questionsList(self):
        return ast.literal_eval(self.Questions)


class Response(db.Model):
    __tablename__ = 'Response'

    ResponseId = db.Column(db.Integer, primary_key=True)
    BeneficiaryId = db.Column(db.String(36), db.ForeignKey('Beneficiary.BeneficiaryId'), nullable=False)
    SurveyId = db.Column(db.Integer, db.ForeignKey('Survey.SurveyId', ondelete='CASCADE'), nullable=False)
    QuestionId = db.Column(db.Integer, db.ForeignKey('Question.QuestionId'), nullable=False)
    Text = db.Column(db.Text)
    Num = db.Column(db.Integer)
    Beneficiary = db.relationship("Beneficiary", back_populates="SurveyResponse")
    Survey = db.relationship("Survey", back_populates="Response", passive_deletes=True)
    Question = db.relationship("Question", back_populates="Response")

    def responsesList(self):
        return ast.literal_eval(self.Responses)
    
class Attendance(db.Model):
    __tablename__ = 'Attendance'

    AttendanceId = db.Column(db.Integer, primary_key=True)
    HasAttended = db.Column(db.Boolean, default=False)
    BeneficiaryId = db.Column(db.String(36), db.ForeignKey('Beneficiary.BeneficiaryId'), nullable=False)
    ActivityId = db.Column(db.Integer, db.ForeignKey('Activity.ActivityId', ondelete='CASCADE'), nullable=False)
    Activity = db.relationship("Activity", back_populates="Attendance", passive_deletes=True)
    Beneficiary = db.relationship("Beneficiary", back_populates="Attendance")

class Certificate(db.Model):
    __tablename__ = 'Certificate'

    CertificateId = db.Column(db.Integer, primary_key=True)
    CertificateUrl = db.Column(db.Text)
    CertificateFileId = db.Column(db.Text)
    UserId = db.Column(db.String(36), db.ForeignKey('User.UserId'), nullable=False)
    ProjectId = db.Column(db.Integer, db.ForeignKey('Project.ProjectId', ondelete='CASCADE'), nullable=False)
    User = db.relationship("User", back_populates="Certificate", passive_deletes=True)
    Project = db.relationship("Project", back_populates="Certificate")

