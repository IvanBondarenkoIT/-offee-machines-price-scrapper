"""
Custom decorators
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(role):
    """
    Decorator to require specific user role
    
    Usage:
        @role_required('admin')
        def admin_only_view():
            pass
    
    Args:
        role: Required role ('admin', 'manager', 'viewer')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.role != role:
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator to require admin role
    
    Usage:
        @admin_required
        def admin_view():
            pass
    """
    return role_required('admin')(f)

