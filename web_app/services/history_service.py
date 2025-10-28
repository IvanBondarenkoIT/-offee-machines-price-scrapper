"""
History service - uploads history and trends
"""
from web_app.models import Upload, Product, CompetitorPrice, Statistic
from web_app.database import db
from sqlalchemy import func

def get_all_uploads():
    """
    Get all uploads with statistics
    
    Returns:
        list: uploads with statistics
    """
    uploads = Upload.query.order_by(Upload.upload_date.desc()).all()
    
    result = []
    for upload in uploads:
        statistics = Statistic.query.filter_by(upload_id=upload.id).first()
        
        result.append({
            'upload': upload,
            'statistics': statistics
        })
    
    return result

def get_upload_details(upload_id):
    """
    Get detailed information about specific upload
    
    Args:
        upload_id: Upload ID
    
    Returns:
        dict: upload details
    """
    upload = Upload.query.get(upload_id)
    
    if not upload:
        raise Exception(f"Upload not found: {upload_id}")
    
    statistics = Statistic.query.filter_by(upload_id=upload.id).first()
    products_count = Product.query.filter_by(upload_id=upload.id).count()
    
    return {
        'upload': {
            'id': upload.id,
            'date': upload.upload_date.isoformat(),
            'uploaded_at': upload.uploaded_at.isoformat(),
            'file_name': upload.file_name,
            'total_products': upload.total_products,
            'status': upload.status
        },
        'statistics': {
            'total_value': float(statistics.total_value) if statistics else 0,
            'avg_price': float(statistics.avg_price) if statistics else 0,
            'products_cheaper': statistics.products_cheaper if statistics else 0,
            'products_expensive': statistics.products_expensive if statistics else 0,
            'products_no_competitors': statistics.products_no_competitors if statistics else 0
        } if statistics else None,
        'products_count': products_count
    }

def get_price_trends(model):
    """
    Get price trends for a specific product model over time
    
    Args:
        model: Product model string
    
    Returns:
        dict: price trends data
    """
    # Get all products with this model
    products = (
        Product.query
        .join(Upload, Product.upload_id == Upload.id)
        .filter(Product.model == model)
        .order_by(Upload.upload_date)
        .all()
    )
    
    if not products:
        raise Exception(f"No data found for model: {model}")
    
    # Build trends data
    trends = []
    
    for product in products:
        upload = Upload.query.get(product.upload_id)
        competitor_prices = CompetitorPrice.query.filter_by(product_id=product.id).all()
        
        # Organize competitor prices
        competitors_data = {}
        for cp in competitor_prices:
            competitors_data[cp.competitor] = {
                'price': float(cp.price),
                'has_discount': cp.has_discount,
                'regular_price': float(cp.regular_price) if cp.regular_price else None,
                'discount_price': float(cp.discount_price) if cp.discount_price else None
            }
        
        trends.append({
            'date': upload.upload_date.isoformat(),
            'our_price': float(product.our_price),
            'quantity': product.quantity,
            'competitors': competitors_data
        })
    
    return {
        'model': model,
        'name': products[0].name if products else None,
        'brand': products[0].brand if products else None,
        'trends': trends
    }

