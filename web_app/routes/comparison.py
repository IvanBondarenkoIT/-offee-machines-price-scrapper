"""
Price comparison routes
"""
from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required
from web_app.models import Upload
from web_app.services.comparison_service import (
    get_latest_comparison,
    get_comparison_by_date,
    filter_products,
    export_to_excel
)
from web_app.services.report_service import generate_pdf_report

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
    """Export comparison to Excel and download"""
    try:
        excel_file = export_to_excel(upload_id)
        upload = Upload.query.get(upload_id)
        date_str = upload.upload_date.strftime('%Y%m%d') if upload else 'export'
        filename = f'price_comparison_{date_str}.xlsx'
        
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@bp.route('/report/<int:upload_id>')
@login_required
def report(upload_id):
    """Generate PDF report with recommendations"""
    try:
        pdf_file = generate_pdf_report(upload_id)
        upload = Upload.query.get(upload_id)
        date_str = upload.upload_date.strftime('%Y%m%d') if upload else 'report'
        filename = f'executive_report_{date_str}.pdf'
        
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

