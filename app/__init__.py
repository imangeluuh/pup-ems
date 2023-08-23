from flask import Flask
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://pup:pup123@localhost:5432/pup-ems"
app.config['SECRET_KEY'] = '95cb72ceb2b65d63f4195f84'
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# route where user will be redirected if not logged in
# login_manager.login_view = [enter route here]
from app import views, models
from .admin.admin import admin_bp
from .auth.auth import auth_bp
from .projects.projects import projects_bp


app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp, url_prefix="/auth") 
app.register_blueprint(projects_bp, url_prefix='/') 
