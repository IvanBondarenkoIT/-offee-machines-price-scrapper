"""
Main routes - Dashboard
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from web_app.services.dashboard_service import get_dashboard_data

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page - redirect to dashboard"""
    return redirect(url_for('main.dashboard'))

@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page"""
    try:
        # Get dashboard data from service
        data = get_dashboard_data()
        
        return render_template(
            'dashboard/index.html',
            latest_upload=data['latest_upload'],
            statistics=data['statistics'],
            top_products=data['top_products'],
            recent_uploads=data['recent_uploads']
        )
    except Exception as e:
        # If no data available, show empty dashboard
        return render_template(
            'dashboard/index.html',
            latest_upload=None,
            statistics=None,
            top_products=[],
            recent_uploads=[],
            error=str(e)
        )

