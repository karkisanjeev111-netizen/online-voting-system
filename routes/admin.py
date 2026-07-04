python
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