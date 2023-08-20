from app import db

class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(14), nullable=False)
    login = db.relationship("Login", backref='login', lazy=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"{self.name}"


class Login(db.Model):
    __tablename__ = 'login'

    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    status = db.Column(db.String(20), default='Active')
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    admin_login = db.relationship("Admin", backref='admin_login', lazy=True)
    parti_login = db.relationship("Participant", backref='parti_login', lazy=True)

    def __init__(self, id, email, password, role_id):
        self.id = id
        self.email = email
        self.password = password
        self.role_id = role_id

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


class Participant(db.Model):
    __tablename__ = 'participant'

    id = db.Column(db.String(36), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), default=None)
    last_name = db.Column(db.String(50), nullable=False)
    contact_details = db.Column(db.String(13), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    login_id = db.Column(db.String(36), db.ForeignKey('login.id'), nullable=False)

    def __init__(self, id, first_name, middle_name, last_name, contact_details,
                    birthdate, gender, address, login_id):
        self.id = id
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.contact_details = contact_details
        self.birthdate = birthdate
        self.gender = gender
        self.address = address
        self.login_id = login_id

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"

