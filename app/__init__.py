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
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://pup:pup123@localhost:5432/pup-ems"
app.config['SECRET_KEY'] = '95cb72ceb2b65d63f4195f84'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=1)
# app.config['SESSION_PROTECTION'] = 'strong' # not sure
api = Api(app, doc='/docs')
jwt = JWTManager(app)
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
ckeditor = CKEditor(app)
CORS(app)
# route where user will be redirected if not logged in
# login_manager.login_view = [enter route here]
# limiter = Limiter(get_remote_address, app=app, default_limits=['5 per day'])

from app import views, models
# from app.api import bp as api_bp
from .Api.resources import ns
api.add_namespace(ns)

from .admin.admin import bp as admin_bp
app.register_blueprint(admin_bp, url_prefix="/admin")

from .auth.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix="/auth") 

from .programs.programs import bp as programs_bp
app.register_blueprint(programs_bp, url_prefix='/') 

from .announcement.announcement import bp as announcement_bp
app.register_blueprint(announcement_bp, url_prefix='/') 
