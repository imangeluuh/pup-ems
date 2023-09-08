from app import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Login.query.get(user_id)


class Role(db.Model):
    __tablename__ = 'Role'

    RoleId = db.Column(db.Integer, primary_key=True)
    RoleName = db.Column(db.String(14), nullable=False)
    Login = db.relationship("Login", backref='Role', lazy=True, passive_deletes=True)


class Login(db.Model, UserMixin):
    __tablename__ = 'Login'

    LoginId = db.Column(db.String(36), primary_key=True)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    Password = db.Column(db.String(60), nullable=False)
    Status = db.Column(db.String(20), default='Active')
    RoleId = db.Column(db.Integer, db.ForeignKey('Role.RoleId', ondelete='CASCADE'), nullable=False)
    AdminLogin = db.relationship("Admin", backref='AdminLogin', lazy=True, passive_deletes=True)
    UserLogin = db.relationship("User", backref='UserLogin', lazy=True, passive_deletes=True)

    @property
    def password_hash(self):
        return self.password_hash
    

    @password_hash.setter
    def password_hash(self, plain_text_password):
        self.Password = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')


    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.Password, attempted_password)
    

    def get_id(self):
        return (self.LoginId)



class Admin(db.Model):
    __tablename__ = 'Admin'

    AdminId = db.Column(db.String(36), primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    LoginId = db.Column(db.String(36), db.ForeignKey('Login.LoginId', ondelete='CASCADE'), nullable=False)


class User(db.Model):
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
    Status = db.Column(db.String(20), nullable=False)
    AgendaId = db.Column(db.Integer, db.ForeignKey('Agenda.AgendaId', ondelete='CASCADE'), nullable=False)
    Agenda = db.relationship("Agenda", backref='ExtensionProgram', lazy=True, passive_deletes=True)
    ProgramId = db.Column(db.Integer, db.ForeignKey('Program.ProgramId', ondelete='CASCADE'), nullable=False)
    Program = db.relationship("Program", backref='ExtensionProgram', lazy=True, passive_deletes=True)
    Project = db.relationship("Project", backref='ExtensionProgram', lazy=True, passive_deletes=True)


class Project(db.Model):
    __tablename__ = 'Project'

    ProjectId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    LeadProponent = db.Column(db.String(255), nullable=False) # Can be integer for FacultyID foreign key
    ProjectType = db.Column(db.String(100), nullable=False)
    Rationale = db.Column(db.String(255), nullable=False)
    Objectives = db.Column(db.String(255), nullable=False)
    StartDate = db.Column(db.Date)
    NumberOfBeneficiaries = db.Column(db.Integer, nullable=False)
    BeneficiariesClassifications = db.Column(db.String(255), nullable=False)
    ProjectScope = db.Column(db.String(255), nullable=False)
    ExtensionProgramId = db.Column(db.Integer, db.ForeignKey('ExtensionProgram.ExtensionProgramId', ondelete='CASCADE'), nullable=False)
    Registration = db.relationship('Registration', backref='Project', cascade='all, delete-orphan', passive_deletes=True)
    # CommunityAssessment =
    # MOU/MOAAssessment = 


class Program(db.Model):
    __tablename__ = 'Program'

    ProgramId = db.Column(db.Integer, primary_key=True)
    ProgramName = db.Column(db.String(255), nullable=False)
    

class Agenda(db.Model):
    __tablename__ = 'Agenda'

    AgendaId = db.Column(db.Integer, primary_key=True)
    AgendaName = db.Column(db.String(255), nullable=False)


class Activity(db.Model):
    __tablename__ = 'Activity'

    ActivityId = db.Column(db.Integer, primary_key=True)
    Date = db.Column(db.Date, nullable=False)
    Duration = db.Column(db.String(255), nullable=False)
    CommunityBackground = db.Column(db.String(255), nullable=False)
    ActivityFlow = db.Column(db.String(255), nullable=False)


class Announcement(db.Model):
    __tablename__ = 'Announcement'

    AnnouncementId = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(255), nullable=False)
    Content= db.Column(db.Text)
    CreatorId = db.Column(db.String(36), db.ForeignKey('Admin.AdminId', ondelete='CASCADE'), nullable=False)
    IsLive = db.Column(db.Boolean, nullable=False)
    Slug = db.Column(db.String(255), nullable=False)
    Created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    Updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    ProjectId = db.Column(db.Integer, db.ForeignKey('Project.ProjectId', ondelete='CASCADE'), nullable=False)
    Project = db.relationship('Project', backref='Announcement')
    Creator = db.relationship('Admin', backref='Announcement')


class Registration(db.Model):
    __tablename__ = 'Registration'

    RegistrationId = db.Column(db.Integer, primary_key=True)
    RegistrationDate = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    ProjectId = db.Column(db.Integer, db.ForeignKey('Project.ProjectId', ondelete='CASCADE'), nullable=False)
    UserId = db.Column(db.String(36), db.ForeignKey('User.UserId', ondelete='CASCADE'), nullable=False)