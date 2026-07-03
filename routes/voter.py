from flask import Blueprint, render_template
from flask_login import login_required

voter_bp = Blueprint('voter', __name__)

@voter_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@voter_bp.route('/vote')
@login_required
def vote():
    return render_template('vote.html')

@voter_bp.route('/about')
def about():
    return render_template('about.html')

@voter_bp.route('/contact')
def contact():
    return render_template('contact.html')