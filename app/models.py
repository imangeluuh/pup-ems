from app import db

class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=14), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"{self.name}"


class Login(db.Model):
    __tablename__ = 'login'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(length=100), nullable=False, unique=True)
    password = db.Column(db.String(length=36), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship("Role", backref=db.backref("role", uselist=False))

    def __init__(self, email, password, role_id):
        self.email = email
        self.password = password
        self.role_id = role_id

    def __repr__(self):
        return f"{self.email}"


class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Uuid, primary_key=True)
    first_name = db.Column(db.String(length=50), nullable=False)
    last_name = db.Column(db.String(length=50), nullable=False)
    login_id = db.Column(db.Integer, db.ForeignKey('login.id'), nullable=False)
    login = db.relationship("Login", backref=db.backref("login", uselist=False))

    def __init__(self, first_name, last_name, login_id):
        self.first_name = first_name
        self.last_name = last_name
        self.login_id = login_id

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"