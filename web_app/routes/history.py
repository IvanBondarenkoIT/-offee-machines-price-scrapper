"""
History routes - all uploads
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from web_app.services.history_service import (
    get_all_uploads,
    get_upload_details,
    get_price_trends
)

bp = Blueprint('history', __name__, url_prefix='/history')

@bp.route('/')
@login_required
def index():
    """History page - all uploads"""
    try:
        uploads = get_all_uploads()
        
        return render_template(
            'history/index.html',
            uploads=uploads
        )
    except Exception as e:
        return render_template(
            'history/index.html',
            uploads=[],
            error=str(e)
        )

@bp.route('/details/<int:upload_id>')
@login_required
def details(upload_id):
    """Upload details (AJAX)"""
    try:
        details = get_upload_details(upload_id)
        
        return jsonify({
            'success': True,
            'upload': details['upload'],
            'statistics': details['statistics'],
            'products_count': details['products_count']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@bp.route('/trends/<model>')
@login_required
def trends(model):
    """Price trends for a product (AJAX)"""
    try:
        trends_data = get_price_trends(model)
        
        return jsonify({
            'success': True,
            'model': model,
            'data': trends_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

