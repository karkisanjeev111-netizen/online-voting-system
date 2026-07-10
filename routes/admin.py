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


# ---------- Dashboard ----------
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


# ---------- Elections ----------
@admin_bp.route('/elections')
@login_required
@admin_required
def manage_elections():
    elections = Election.query.order_by(Election.created_at.desc()).all()
    return render_template('admin/manage_elections.html', elections=elections)


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


@admin_bp.route('/elections/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_election(id):
    election = Election.query.get_or_404(id)
    if request.method == 'POST':
        election.title = request.form.get('title')
        election.description = request.form.get('description')
        election.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M')
        election.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%dT%H:%M')
        election.is_active = 'is_active' in request.form
        db.session.commit()
        flash('Election updated.', 'success')
        return redirect(url_for('admin.manage_elections'))
    return render_template('admin/edit_election.html', election=election)


@admin_bp.route('/elections/delete/<int:id>')
@login_required
@admin_required
def delete_election(id):
    election = Election.query.get_or_404(id)
    Vote.query.filter_by(election_id=id).delete()
    Candidate.query.filter_by(election_id=id).delete()
    db.session.delete(election)
    db.session.commit()
    flash('Election deleted.', 'success')
    return redirect(url_for('admin.manage_elections'))


# ---------- Candidates ----------
@admin_bp.route('/candidates')
@login_required
@admin_required
def manage_candidates():
    candidates = Candidate.query.order_by(Candidate.election_id).all()
    return render_template('admin/manage_candidates.html', candidates=candidates)


@admin_bp.route('/candidates/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_candidate():
    elections = Election.query.filter_by(is_active=True).all()
    if request.method == 'POST':
        name = request.form.get('name')
        party = request.form.get('party')
        description = request.form.get('description')
        election_id = request.form.get('election_id')
        candidate = Candidate(name=name, party=party, description=description, election_id=election_id)
        db.session.add(candidate)
        db.session.commit()
        flash('Candidate added successfully!', 'success')
        return redirect(url_for('admin.manage_candidates'))
    return render_template('admin/create_candidate.html', elections=elections)


@admin_bp.route('/candidates/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_candidate(id):
    candidate = Candidate.query.get_or_404(id)
    elections = Election.query.all()
    if request.method == 'POST':
        candidate.name = request.form.get('name')
        candidate.party = request.form.get('party')
        candidate.description = request.form.get('description')
        candidate.election_id = request.form.get('election_id')
        db.session.commit()
        flash('Candidate updated.', 'success')
        return redirect(url_for('admin.manage_candidates'))
    return render_template('admin/edit_candidate.html', candidate=candidate, elections=elections)


@admin_bp.route('/candidates/delete/<int:id>')
@login_required
@admin_required
def delete_candidate(id):
    candidate = Candidate.query.get_or_404(id)
    Vote.query.filter_by(candidate_id=id).delete()
    db.session.delete(candidate)
    db.session.commit()
    flash('Candidate deleted.', 'success')
    return redirect(url_for('admin.manage_candidates'))


# ---------- Voters ----------
@admin_bp.route('/voters')
@login_required
@admin_required
def manage_voters():
    voters = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/manage_voters.html', voters=voters)


@admin_bp.route('/voters/delete/<int:id>')
@login_required
@admin_required
def delete_voter(id):
    voter = User.query.get_or_404(id)
    if voter.is_admin:
        flash('Cannot delete admin users.', 'danger')
        return redirect(url_for('admin.manage_voters'))
    Vote.query.filter_by(user_id=id).delete()
    db.session.delete(voter)
    db.session.commit()
    flash('Voter deleted.', 'success')
    return redirect(url_for('admin.manage_voters'))