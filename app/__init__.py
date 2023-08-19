from flask import Flask, render_template
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .admin.admin import admin_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://pup:pup123@localhost:5432/pup-ems"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models

app.register_blueprint(admin_bp, url_prefix="/admin")
