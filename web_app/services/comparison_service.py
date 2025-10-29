"""
Comparison service - price comparison data
"""
import pandas as pd
from pathlib import Path
from io import BytesIO
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
    Export comparison to Excel file with full structure (same as local version)
    
    Args:
        upload_id: Upload ID
    
    Returns:
        BytesIO: Excel file as BytesIO object
    """
    upload = Upload.query.get(upload_id)
    
    if not upload:
        raise Exception(f"Upload not found: {upload_id}")
    
    # Get all products and data for this upload
    products = Product.query.filter_by(upload_id=upload_id).order_by(Product.model).all()
    statistics = Statistic.query.filter_by(upload_id=upload_id).first()
    
    # Get all unique competitors
    competitors = (
        db.session.query(CompetitorPrice.competitor)
        .join(Product, CompetitorPrice.product_id == Product.id)
        .filter(Product.upload_id == upload_id)
        .distinct()
        .order_by(CompetitorPrice.competitor)
        .all()
    )
    competitor_names = [c[0] for c in competitors]
    
    # Build main comparison table
    comparison_rows = []
    for product in products:
        row = {
            'Quantity': product.quantity or 0,
            'Model': product.model or '-',
            'Product Name': product.name or '-',
            'Our Price': float(product.our_price) if product.our_price else 0.0,
        }
        
        # Add competitor prices
        competitor_prices = CompetitorPrice.query.filter_by(product_id=product.id).all()
        prices_by_competitor = {cp.competitor: cp for cp in competitor_prices}
        
        for comp_name in competitor_names:
            if comp_name in prices_by_competitor:
                cp = prices_by_competitor[comp_name]
                if cp.has_discount and cp.regular_price and cp.discount_price:
                    row[comp_name] = f"{float(cp.regular_price):.2f} \\ {float(cp.discount_price):.2f}"
                elif cp.price:
                    row[comp_name] = f"{float(cp.price):.2f}"
                else:
                    row[comp_name] = '-'
            else:
                row[comp_name] = '-'
        
        comparison_rows.append(row)
    
    # Create DataFrame for main comparison
    comparison_df = pd.DataFrame(comparison_rows)
    
    # Create Excel in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Main comparison sheet
        comparison_df.to_excel(writer, sheet_name='Price Comparison', index=False)
        
        # Statistics sheet
        if statistics:
            stats_data = {
                'Total Products': [statistics.total_products or 0],
                'Total Value': [float(statistics.total_value) if statistics.total_value else 0.0],
                'Avg Price': [float(statistics.avg_our_price) if statistics.avg_our_price else 0.0],
                'Products Cheaper': [statistics.products_cheaper or 0],
                'Products Expensive': [statistics.products_expensive or 0],
                'Products No Competitors': [statistics.products_no_competitors or 0],
            }
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        # Individual competitor sheets
        for comp_name in competitor_names:
            comp_products = []
            for product in products:
                cp = CompetitorPrice.query.filter_by(
                    product_id=product.id,
                    competitor=comp_name
                ).first()
                
                if cp:
                    comp_row = {
                        'Product Name': product.name or '-',
                        'Price': float(cp.price) if cp.price else None,
                        'Regular Price': float(cp.regular_price) if cp.regular_price else None,
                        'Discount Price': float(cp.discount_price) if cp.discount_price else None,
                        'Has Discount': cp.has_discount,
                        'URL': cp.url or '-'
                    }
                    comp_products.append(comp_row)
            
            if comp_products:
                comp_df = pd.DataFrame(comp_products)
                comp_df.to_excel(writer, sheet_name=comp_name, index=False)
    
    output.seek(0)
    return output

