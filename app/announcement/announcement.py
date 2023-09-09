from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, current_user
from ..models import Project, ExtensionProgram, Program, Announcement, Agenda
import calendar
from datetime import datetime
from sqlalchemy import desc
from app import db

announcement_bp = Blueprint('announcement', __name__, template_folder="templates", static_folder="static", static_url_path='static')

@announcement_bp.route('/announcement')
def announcement():
    announcements = Announcement.query.order_by(desc(Announcement.Updated)).all()
    return render_template('announcement/announcements.html', announcements=announcements)

@announcement_bp.route('/announcement/<int:id>')
def viewAnnouncement(id):
    announcement = Announcement.query.get_or_404(id)
    return render_template('announcement/view_announcement.html', announcement=announcement)
