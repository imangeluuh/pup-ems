from flask import Flask
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from flask_ckeditor import CKEditor

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://pup:pup123@localhost:5432/pup-ems"
app.config['SECRET_KEY'] = '95cb72ceb2b65d63f4195f84'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=1)
# app.config['SESSION_PROTECTION'] = 'strong' # not sure
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
ckeditor = CKEditor(app)
# route where user will be redirected if not logged in
# login_manager.login_view = [enter route here]
# limiter = Limiter(get_remote_address, app=app, default_limits=['5 per day'])

from app import views, models
from .admin.admin import admin_bp
from .auth.auth import auth_bp
from .programs.programs import programs_bp


app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp, url_prefix="/auth") 
app.register_blueprint(programs_bp, url_prefix='/') 
