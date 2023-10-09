from flask import url_for
from app import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
from time import time
from flask_jwt_extended import create_access_token, decode_token

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
    AgendaId = db.Column(db.Integer, db.ForeignKey('Agenda.AgendaId', ondelete='CASCADE'), nullable=False)
    Agenda = db.relationship("Agenda", backref='ExtensionProgram', lazy=True, passive_deletes=True)
    ProgramId = db.Column(db.Integer, db.ForeignKey('Program.ProgramId', ondelete='CASCADE'), nullable=False)
    Program = db.relationship("Program", backref='ExtensionProgram', lazy=True, passive_deletes=True)
    Project = db.relationship("Project", backref='ExtensionProgram', lazy=True, passive_deletes=True)


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
    Registration = db.relationship('Registration', backref='Project', cascade='all, delete-orphan', passive_deletes=True)
    LeadProponent = db.relationship('User', backref='Project', lazy=True, passive_deletes=True)
    # CommunityAssessment =
    # MOU/MOAAssessment = 


class Program(db.Model):
    __tablename__ = 'Program'

    ProgramId = db.Column(db.Integer, primary_key=True)
    ProgramName = db.Column(db.String(255), nullable=False)
    Abbreviation = db.Column(db.String(255), nullable=False)


class Agenda(db.Model):
    __tablename__ = 'Agenda'

    AgendaId = db.Column(db.Integer, primary_key=True)
    AgendaName = db.Column(db.String(255), nullable=False)


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
    Project = db.relationship('Project', backref='Activity')


class Announcement(db.Model):
    __tablename__ = 'Announcement'

    AnnouncementId = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(255), nullable=False)
    Content= db.Column(db.Text)
    CreatorId = db.Column(db.String(36), db.ForeignKey('Admin.AdminId', ondelete='CASCADE'), nullable=False)
    IsLive = db.Column(db.Boolean, index=True, nullable=False)
    Slug = db.Column(db.String(255), nullable=False)
    Created = db.Column(db.DateTime, default=datetime.utcnow, index=True, nullable=False)
    Updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True, nullable=False)
    ProjectId = db.Column(db.Integer, db.ForeignKey('Project.ProjectId', ondelete='CASCADE'), nullable=False)
    Project = db.relationship('Project', backref='Announcement')
    Creator = db.relationship('Admin', backref='Announcement')


class Registration(db.Model):
    __tablename__ = 'Registration'

    RegistrationId = db.Column(db.Integer, primary_key=True)
    RegistrationDate = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    ProjectId = db.Column(db.Integer, db.ForeignKey('Project.ProjectId', ondelete='CASCADE'), nullable=False)
    UserId = db.Column(db.String(36), db.ForeignKey('User.UserId', ondelete='CASCADE'), nullable=False)