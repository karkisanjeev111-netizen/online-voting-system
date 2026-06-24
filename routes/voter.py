from flask import Blueprint, render_template
from flask_login import login_required, current_user

voter_bp = Blueprint('voter', __name__)

@voter_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@voter_bp.route('/vote')
@login_required
def vote():
    return render_template('vote.html')
