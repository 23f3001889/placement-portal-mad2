from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Student, PlacementDrive, Application, Placement
from functools import wraps
import os
from werkzeug.utils import secure_filename
from models import db, Student, PlacementDrive, Application, Placement

student_bp = Blueprint('student', __name__, url_prefix='/student')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not isinstance(current_user, Student):
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        if current_user.is_blacklisted:
            flash('Your account has been blacklisted. Contact admin.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    # All approved drives the student hasn't applied to yet
    applied_drive_ids = [a.drive_id for a in current_user.applications]

    available_drives = PlacementDrive.query.filter_by(
        status='Approved'
    ).filter(
        ~PlacementDrive.id.in_(applied_drive_ids)
    ).order_by(PlacementDrive.created_at.desc()).all()

    # Drives the student has applied to
    applications = Application.query.filter_by(
        student_id=current_user.id
    ).order_by(Application.applied_at.desc()).all()

    return render_template('student/dashboard.html',
        student=current_user,
        available_drives=available_drives,
        applications=applications
    )

@student_bp.route('/drives')
@login_required
@student_required
def drives():
    q = request.args.get('q', '').strip()
    applied_drive_ids = [a.drive_id for a in current_user.applications]

    query = PlacementDrive.query.filter_by(status='Approved')
    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(
                PlacementDrive.job_title.ilike(like),
                PlacementDrive.required_skills.ilike(like),
                PlacementDrive.location.ilike(like),
            )
        )
    drives = query.order_by(PlacementDrive.created_at.desc()).all()
    return render_template('student/drives.html',
        drives=drives,
        applied_drive_ids=applied_drive_ids,
        q=q
    )