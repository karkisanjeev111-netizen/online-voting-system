from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.election import Election
from models.candidate import Candidate
from models.vote import Vote
from app import db
from datetime import datetime

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

@voter_bp.route('/results')
def view_results():
    return render_template('results.html')