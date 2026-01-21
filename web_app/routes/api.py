"""
API routes for data upload
"""
from flask import Blueprint, request, jsonify
from functools import wraps
from web_app.services.upload_service import process_upload
import os

bp = Blueprint('api', __name__, url_prefix='/api')

def require_api_key(f):
    """Decorator to require API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key is required'
            }), 401
        
        # Get expected API key from config
        expected_key = os.environ.get('API_KEY')
        
        if api_key != expected_key:
            return jsonify({
                'success': False,
                'error': 'Invalid API key'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/upload', methods=['POST'])
@require_api_key
def upload():
    """
    Upload Excel file with price comparison data
    
    Expected: multipart/form-data with 'file' field
    Headers: X-API-Key: <your_api_key>
    
    Returns:
        JSON with upload status and statistics
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if file has a name
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file extension
        if not file.filename.endswith('.xlsx'):
            return jsonify({
                'success': False,
                'error': 'Only .xlsx files are accepted'
            }), 400
        
        # Process upload
        result = process_upload(file)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'upload_id': result['upload_id'],
            'upload_date': result['upload_date'],
            'statistics': result['statistics']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Coffee Price Monitor API'
    })

@bp.route('/uploads', methods=['GET'])
@require_api_key
def list_uploads():
    """List all uploads (for uploader script)"""
    try:
        from web_app.models import Upload
        
        uploads = Upload.query.order_by(Upload.upload_date.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'uploads': [
                {
                    'id': u.id,
                    'date': u.upload_date.isoformat(),
                    'status': u.status,
                    'products': u.total_products
                }
                for u in uploads
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

