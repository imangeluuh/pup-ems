from app.announcement import bp
from flask import render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, current_user
from ..models import Project, ExtensionProgram, Program, Announcement, Agenda
import calendar
from datetime import datetime
from sqlalchemy import desc
from app import db

@bp.route('/announcement')
def announcement():
    announcements = Announcement.query.order_by(desc(Announcement.Updated)).all()
    return render_template('announcement/announcements.html', announcements=announcements)

@bp.route('/announcement/<int:id>')
def viewAnnouncement(id):
    announcement = Announcement.query.get_or_404(id)
    return render_template('announcement/view_announcement.html', announcement=announcement)
