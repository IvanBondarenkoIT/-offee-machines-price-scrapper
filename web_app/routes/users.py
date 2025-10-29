"""
User management routes (admin only)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from web_app.models import User
from web_app.database import db
from web_app.utils.decorators import admin_required
from datetime import datetime
from flask_babel import gettext as _

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/')
@login_required
@admin_required
def index():
    """List all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users/index.html', users=users)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new user"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'viewer')
        
        # Validation
        if not username or not email or not password:
            flash(_('Please fill all required fields'), 'danger')
            return render_template('users/form.html', user=None, action='create')
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash(_('Username or email already exists'), 'danger')
            return render_template('users/form.html', user=None, action='create')
        
        # Create user
        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(_('User created successfully'), 'success')
        return redirect(url_for('users.index'))
    
    return render_template('users/form.html', user=None, action='create')

@bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(user_id):
    """Edit user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent editing yourself's role
    if user.id == current_user.id and request.method == 'POST':
        flash(_('You cannot change your own role'), 'warning')
        return redirect(url_for('users.edit', user_id=user_id))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', user.role)
        
        # Validation
        if not username or not email:
            flash(_('Please fill all required fields'), 'danger')
            return render_template('users/form.html', user=user, action='edit')
        
        # Check if username or email already exists (excluding current user)
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).filter(User.id != user_id).first()
        
        if existing_user:
            flash(_('Username or email already exists'), 'danger')
            return render_template('users/form.html', user=user, action='edit')
        
        # Update user
        user.username = username
        user.email = email
        user.role = role
        
        # Update password if provided
        if password:
            user.set_password(password)
        
        db.session.commit()
        
        flash(_('User updated successfully'), 'success')
        return redirect(url_for('users.index'))
    
    return render_template('users/form.html', user=user, action='edit')

@bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash(_('You cannot delete your own account'), 'danger')
        return redirect(url_for('users.index'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(_('User %(username)s deleted successfully', username=username), 'success')
    return redirect(url_for('users.index'))

