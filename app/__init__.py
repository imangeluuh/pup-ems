from flask import Flask, render_template
from blueprints.main import main
from blueprints.admin.auth import auth
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://pup:pup123@localhost:5432/pup-ems"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models

app.register_blueprint(main)
app.register_blueprint(auth, url_prefix="/admin")