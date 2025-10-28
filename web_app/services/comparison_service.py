"""
Comparison service - price comparison data
"""
from web_app.models import Upload, Product, CompetitorPrice, Statistic
from web_app.database import db
from datetime import datetime
from sqlalchemy import and_, or_

def get_latest_comparison():
    """
    Get latest price comparison data
    
    Returns:
        dict: {
            'upload': Upload object,
            'products': list of products with competitors,
            'statistics': Statistic object,
            'competitors': list of competitor names
        }
    """
    # Get latest upload
    upload = Upload.query.order_by(Upload.upload_date.desc()).first()
    
    if not upload:
        raise Exception("No data available")
    
    return _get_comparison_data(upload)

def get_comparison_by_date(date_str):
    """
    Get price comparison for specific date
    
    Args:
        date_str: Date string in format YYYY-MM-DD
    
    Returns:
        dict: comparison data
    """
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise Exception(f"Invalid date format: {date_str}")
    
    upload = Upload.query.filter_by(upload_date=date).first()
    
    if not upload:
        raise Exception(f"No data found for date: {date_str}")
    
    return _get_comparison_data(upload)

def _get_comparison_data(upload):
    """
    Get comparison data for specific upload
    
    Args:
        upload: Upload object
    
    Returns:
        dict: comparison data
    """
    # Get all products for this upload
    products = Product.query.filter_by(upload_id=upload.id).all()
    
    # Get statistics
    statistics = Statistic.query.filter_by(upload_id=upload.id).first()
    
    # Get all unique competitors
    competitors = (
        db.session.query(CompetitorPrice.competitor)
        .join(Product, CompetitorPrice.product_id == Product.id)
        .filter(Product.upload_id == upload.id)
        .distinct()
        .all()
    )
    competitor_names = [c[0] for c in competitors]
    
    # Format products with their competitor prices
    formatted_products = []
    for product in products:
        competitor_prices = CompetitorPrice.query.filter_by(product_id=product.id).all()
        
        # Organize competitor prices by competitor name
        prices_by_competitor = {}
        for cp in competitor_prices:
            prices_by_competitor[cp.competitor] = cp
        
        formatted_products.append({
            'product': product,
            'competitor_prices': prices_by_competitor
        })
    
    return {
        'upload': upload,
        'products': formatted_products,
        'statistics': statistics,
        'competitors': competitor_names
    }

def filter_products(upload_id, filters):
    """
    Filter products based on criteria
    
    Args:
        upload_id: Upload ID
        filters: dict with filter criteria
    
    Returns:
        list: filtered products
    """
    query = Product.query.filter_by(upload_id=upload_id)
    
    # Brand filter
    if filters.get('brand'):
        query = query.filter(Product.brand == filters['brand'])
    
    # Price range
    if filters.get('price_from'):
        query = query.filter(Product.our_price >= float(filters['price_from']))
    
    if filters.get('price_to'):
        query = query.filter(Product.our_price <= float(filters['price_to']))
    
    # Search by model or name
    if filters.get('search'):
        search_term = f"%{filters['search']}%"
        query = query.filter(
            or_(
                Product.model.ilike(search_term),
                Product.name.ilike(search_term)
            )
        )
    
    products = query.all()
    
    # Additional filters that require competitor data
    if any([filters.get('cheaper'), filters.get('more_expensive'), filters.get('no_competitors'), filters.get('competitor')]):
        filtered_products = []
        
        for product in products:
            competitor_prices = CompetitorPrice.query.filter_by(product_id=product.id).all()
            
            # No competitors filter
            if filters.get('no_competitors') and len(competitor_prices) > 0:
                continue
            
            # Specific competitor filter
            if filters.get('competitor'):
                has_competitor = any(cp.competitor == filters['competitor'] for cp in competitor_prices)
                if not has_competitor:
                    continue
            
            # Cheaper/more expensive filter
            if filters.get('cheaper') or filters.get('more_expensive'):
                if len(competitor_prices) == 0:
                    continue
                
                # Check if we are cheaper or more expensive
                is_cheaper = any(product.our_price < cp.price for cp in competitor_prices)
                is_more_expensive = any(product.our_price > cp.price for cp in competitor_prices)
                
                if filters.get('cheaper') and not is_cheaper:
                    continue
                if filters.get('more_expensive') and not is_more_expensive:
                    continue
            
            filtered_products.append(product)
        
        products = filtered_products
    
    # Format for JSON response
    result = []
    for product in products:
        competitor_prices = CompetitorPrice.query.filter_by(product_id=product.id).all()
        
        result.append({
            'id': product.id,
            'model': product.model,
            'name': product.name,
            'brand': product.brand,
            'our_price': float(product.our_price),
            'quantity': product.quantity,
            'competitors': [
                {
                    'name': cp.competitor,
                    'price': float(cp.price),
                    'has_discount': cp.has_discount,
                    'regular_price': float(cp.regular_price) if cp.regular_price else None,
                    'discount_price': float(cp.discount_price) if cp.discount_price else None
                }
                for cp in competitor_prices
            ]
        })
    
    return result

def export_to_excel(upload_id):
    """
    Export comparison to Excel file
    
    Args:
        upload_id: Upload ID
    
    Returns:
        str: path to exported file
    """
    # This is a placeholder - actual implementation would generate Excel file
    # For now, we'll just return the original file path if available
    upload = Upload.query.get(upload_id)
    
    if not upload:
        raise Exception(f"Upload not found: {upload_id}")
    
    # TODO: Generate Excel file from database data
    # For now, return the original file name
    return upload.file_name

