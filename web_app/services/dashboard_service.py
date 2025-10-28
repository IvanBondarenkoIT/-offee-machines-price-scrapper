"""
Dashboard service - data for main dashboard
"""
from web_app.models import Upload, Product, CompetitorPrice, Statistic
from web_app.database import db
from sqlalchemy import func, desc

def get_dashboard_data():
    """
    Get data for main dashboard
    
    Returns:
        dict: {
            'latest_upload': Upload object,
            'statistics': Statistic object,
            'top_products': list of products with most competitors,
            'recent_uploads': list of recent uploads
        }
    """
    # Get latest upload
    latest_upload = Upload.query.order_by(Upload.upload_date.desc()).first()
    
    if not latest_upload:
        return {
            'latest_upload': None,
            'statistics': None,
            'top_products': [],
            'recent_uploads': []
        }
    
    # Get statistics for latest upload
    statistics = Statistic.query.filter_by(upload_id=latest_upload.id).first()
    
    # Get top products (by number of competitors)
    top_products = (
        db.session.query(
            Product,
            func.count(CompetitorPrice.id).label('competitor_count')
        )
        .outerjoin(CompetitorPrice, Product.id == CompetitorPrice.product_id)
        .filter(Product.upload_id == latest_upload.id)
        .group_by(Product.id)
        .order_by(desc('competitor_count'))
        .limit(10)
        .all()
    )
    
    # Format top products
    formatted_top_products = []
    for product, count in top_products:
        # Get competitor prices
        competitors = CompetitorPrice.query.filter_by(product_id=product.id).all()
        
        formatted_top_products.append({
            'product': product,
            'competitor_count': count,
            'competitors': competitors
        })
    
    # Get recent uploads (last 5)
    recent_uploads = Upload.query.order_by(Upload.upload_date.desc()).limit(5).all()
    
    return {
        'latest_upload': latest_upload,
        'statistics': statistics,
        'top_products': formatted_top_products,
        'recent_uploads': recent_uploads
    }

