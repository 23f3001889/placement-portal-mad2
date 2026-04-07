from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Admin, Company, Student, PlacementDrive, Application
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not isinstance(current_user, Admin):
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_students  = Student.query.count()
    total_companies = Company.query.count()
    total_drives    = PlacementDrive.query.count()
    total_apps      = Application.query.count()
    pending_companies = Company.query.filter_by(approval_status='Pending').all()
    pending_drives    = PlacementDrive.query.filter_by(status='Pending').all()

    return render_template('admin/dashboard.html',
        total_students=total_students,
        total_companies=total_companies,
        total_drives=total_drives,
        total_apps=total_apps,
        pending_companies=pending_companies,
        pending_drives=pending_drives
    )

# 1) Approve/Reject Companies
@admin_bp.route('/company/<int:company_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'Approved'
    db.session.commit()
    flash(f'{company.company_name} has been approved.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/company/<int:company_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'Rejected'
    db.session.commit()
    flash(f'{company.company_name} has been rejected.', 'warning')
    return redirect(url_for('admin.dashboard'))

# 2) Approve/Reject Drives
@admin_bp.route('/drive/<int:drive_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'Approved'
    db.session.commit()
    flash(f'Drive "{drive.job_title}" approved.', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/drive/<int:drive_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'Rejected'
    db.session.commit()
    flash(f'Drive "{drive.job_title}" rejected.', 'warning')
    return redirect(request.referrer or url_for('admin.dashboard'))

# 3) student
@admin_bp.route('/students')
@login_required
@admin_required
def students():
    q = request.args.get('q', '').strip()
    query = Student.query
    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(
                Student.full_name.ilike(like),
                Student.email.ilike(like),
                Student.phone.ilike(like),
                db.cast(Student.id, db.String).ilike(like),
            )
        )
    students = query.order_by(Student.created_at.desc()).all()
    return render_template('admin/students.html', students=students, q=q)