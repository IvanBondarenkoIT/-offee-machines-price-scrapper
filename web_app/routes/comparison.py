"""
Price comparison routes
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from web_app.services.comparison_service import (
    get_latest_comparison,
    get_comparison_by_date,
    filter_products,
    export_to_excel
)

bp = Blueprint('comparison', __name__, url_prefix='/comparison')

@bp.route('/')
@login_required
def index():
    """Latest price comparison"""
    try:
        data = get_latest_comparison()
        
        return render_template(
            'comparison/index.html',
            upload=data['upload'],
            products=data['products'],
            statistics=data['statistics'],
            competitors=data['competitors']
        )
    except Exception as e:
        return render_template(
            'comparison/index.html',
            upload=None,
            products=[],
            statistics=None,
            competitors=[],
            error=str(e)
        )

@bp.route('/date/<date_str>')
@login_required
def by_date(date_str):
    """Comparison by specific date"""
    try:
        data = get_comparison_by_date(date_str)
        
        return render_template(
            'comparison/index.html',
            upload=data['upload'],
            products=data['products'],
            statistics=data['statistics'],
            competitors=data['competitors']
        )
    except Exception as e:
        return render_template(
            'comparison/index.html',
            upload=None,
            products=[],
            statistics=None,
            competitors=[],
            error=f"No data found for date: {date_str}"
        )

@bp.route('/filter', methods=['POST'])
@login_required
def filter():
    """Filter products (AJAX)"""
    try:
        filters = {
            'brand': request.form.get('brand'),
            'price_from': request.form.get('price_from'),
            'price_to': request.form.get('price_to'),
            'competitor': request.form.get('competitor'),
            'cheaper': request.form.get('cheaper') == 'true',
            'more_expensive': request.form.get('more_expensive') == 'true',
            'no_competitors': request.form.get('no_competitors') == 'true',
            'search': request.form.get('search')
        }
        
        upload_id = request.form.get('upload_id')
        products = filter_products(upload_id, filters)
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@bp.route('/export/<int:upload_id>')
@login_required
def export(upload_id):
    """Export comparison to Excel"""
    try:
        file_path = export_to_excel(upload_id)
        return jsonify({
            'success': True,
            'message': 'Export completed',
            'file': file_path
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

