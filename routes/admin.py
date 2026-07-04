from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from models.election import Election
from models.candidate import Candidate
from models.user import User
from models.vote import Vote
from datetime import datetime

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    elections_count = Election.query.count()
    candidates_count = Candidate.query.count()
    voters_count = User.query.filter_by(is_admin=False).count()
    votes_count = Vote.query.count()
    return render_template('admin/admin_dashboard.html',
                           elections_count=elections_count,
                           candidates_count=candidates_count,
                           voters_count=voters_count,
                           votes_count=votes_count)

@admin_bp.route('/elections')
@login_required
@admin_required
def manage_elections():
    elections = Election.query.order_by(Election.created_at.desc()).all()
    @admin_bp.route('/elections/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_election():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%dT%H:%M')
        election = Election(title=title, description=description,
                            start_date=start_date, end_date=end_date)
        db.session.add(election)
        db.session.commit()
        flash('Election created successfully!', 'success')
        return redirect(url_for('admin.manage_elections'))
    return render_template('admin/create_election.html')
    return render_template('admin/manage_elections.html', elections=elections)