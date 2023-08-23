from app import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Login.query.get(user_id)

class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(14), nullable=False)
    login = db.relationship("Login", backref='login', lazy=True)

    def __repr__(self):
        return f"{self.name}"


class Login(db.Model, UserMixin):
    __tablename__ = 'login'

    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    status = db.Column(db.String(20), default='Active')
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    admin_login = db.relationship("Admin", backref='admin_login', lazy=True)
    user_login = db.relationship("User", backref='user_login', lazy=True)

    @property
    def password_hash(self):
        return self.password_hash
    
    @password_hash.setter
    def password_hash(self, plain_text_password):
        self.password = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password, attempted_password)

    def __repr__(self):
        return f"{self.email}"


class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.String(36), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    login_id = db.Column(db.String(36), db.ForeignKey('login.id'), nullable=False)
    
    def __init__(self, id, first_name, last_name, login_id):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.login_id = login_id

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String(36), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), default=None)
    last_name = db.Column(db.String(50), nullable=False)
    contact_details = db.Column(db.String(13), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    login_id = db.Column(db.String(36), db.ForeignKey('login.id'), nullable=False)
    participant = db.relationship("Participant", backref='participant', lazy=True)
    volunteer = db.relationship("Volunteer", backref='volunteer', lazy=True)

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


class Participant(db.Model):
    __tablename__ = 'participant'

    id = db.Column(db.String(36), db.ForeignKey('user.id'), primary_key=True)


class Volunteer(db.Model):
    __tablename__ = 'volunteer'

    id = db.Column(db.String(36), db.ForeignKey('user.id'), primary_key=True)
    skills_interest = db.Column(db.String(255), nullable=False)
