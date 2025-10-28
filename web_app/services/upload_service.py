"""
Upload service - process Excel file uploads
"""
import pandas as pd
from datetime import datetime, date
from web_app.models import Upload, Product, CompetitorPrice, Statistic, User
from web_app.database import db
from werkzeug.utils import secure_filename
import os

def process_upload(file, user_id=None):
    """
    Process uploaded Excel file
    
    Args:
        file: FileStorage object from Flask request
        user_id: ID of user who uploaded (optional, for API uploads)
    
    Returns:
        dict: upload result with statistics
    """
    # Save file temporarily
    filename = secure_filename(file.filename)
    temp_path = os.path.join('/tmp', filename)
    file.save(temp_path)
    
    try:
        # Read Excel file
        excel_data = pd.read_excel(temp_path, sheet_name=None)
        
        # Get today's date for this upload
        upload_date = date.today()
        
        # Check if upload for today already exists
        existing_upload = Upload.query.filter_by(upload_date=upload_date).first()
        
        if existing_upload:
            # Update existing upload
            upload = existing_upload
            upload.status = 'processing'
            upload.uploaded_at = datetime.utcnow()
            upload.file_name = filename
            
            # Delete old products and related data (cascade will handle competitor_prices)
            Product.query.filter_by(upload_id=upload.id).delete()
            Statistic.query.filter_by(upload_id=upload.id).delete()
            
            db.session.commit()
        else:
            # Create new upload
            upload = Upload(
                upload_date=upload_date,
                uploaded_at=datetime.utcnow(),
                uploaded_by=user_id,
                file_name=filename,
                total_products=0,
                status='processing'
            )
            db.session.add(upload)
            db.session.commit()
        
        # Process data
        result = _process_excel_data(excel_data, upload.id)
        
        # Update upload status
        upload.total_products = result['total_products']
        upload.status = 'completed'
        db.session.commit()
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return {
            'upload_id': upload.id,
            'upload_date': upload.upload_date.isoformat(),
            'statistics': result['statistics']
        }
    
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Update upload status to failed if upload exists
        if 'upload' in locals():
            upload.status = 'failed'
            db.session.commit()
        
        raise e

def _process_excel_data(excel_data, upload_id):
    """
    Process Excel sheets and extract data
    
    Args:
        excel_data: dict of DataFrames (sheet_name: DataFrame)
        upload_id: Upload ID
    
    Returns:
        dict: processing result
    """
    # Get main comparison sheet (usually first sheet or named "Price Comparison")
    main_sheet = None
    
    if 'Price Comparison' in excel_data:
        main_sheet = excel_data['Price Comparison']
    else:
        # Use first sheet
        main_sheet = list(excel_data.values())[0]
    
    # Process main comparison data
    products_data = _parse_comparison_sheet(main_sheet, upload_id)
    
    # Calculate statistics
    statistics = _calculate_statistics(products_data, upload_id)
    
    return {
        'total_products': len(products_data),
        'statistics': statistics
    }

def _parse_comparison_sheet(df, upload_id):
    """
    Parse Price Comparison sheet
    
    Expected columns:
    - Model
    - Product Name
    - Our Price
    - Quantity
    - DIM_KAVA, ALTA, KONTAKT, ELITE, COFFEEHUB, COFFEEPIN, VELI_STORE, VEGA_GE (competitor columns)
    
    Args:
        df: DataFrame with comparison data
        upload_id: Upload ID
    
    Returns:
        list: processed products
    """
    products_data = []
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Competitor columns
    competitor_columns = ['DIM_KAVA', 'ALTA', 'KONTAKT', 'ELITE', 'COFFEEHUB', 'COFFEEPIN', 'VELI_STORE', 'VEGA_GE']
    
    for idx, row in df.iterrows():
        try:
            # Skip empty rows
            if pd.isna(row.get('Model')) or pd.isna(row.get('Our Price')):
                continue
            
            model = str(row['Model']).strip()
            name = str(row.get('Product Name', model))
            our_price = float(row['Our Price'])
            quantity = int(row.get('Quantity', 0))
            
            # Determine brand from model
            brand = _determine_brand(model, name)
            
            # Create product
            product = Product(
                upload_id=upload_id,
                model=model,
                name=name,
                quantity=quantity,
                our_price=our_price,
                brand=brand,
                source='INVENTORY'
            )
            
            db.session.add(product)
            db.session.flush()  # Get product.id
            
            # Process competitor prices
            competitor_count = 0
            
            for competitor in competitor_columns:
                if competitor not in df.columns:
                    continue
                
                price_value = row.get(competitor)
                
                if pd.isna(price_value) or price_value == '-':
                    continue
                
                # Parse price (can be "123.45" or "150.00 \ 120.00" for discount)
                price_str = str(price_value).strip()
                
                if '\\' in price_str:
                    # Has discount
                    parts = price_str.split('\\')
                    regular_price = float(parts[0].strip())
                    discount_price = float(parts[1].strip())
                    price = discount_price
                    has_discount = True
                else:
                    # No discount
                    price = float(price_str)
                    regular_price = price
                    discount_price = None
                    has_discount = False
                
                # Create competitor price
                cp = CompetitorPrice(
                    product_id=product.id,
                    competitor=competitor,
                    price=price,
                    regular_price=regular_price,
                    discount_price=discount_price,
                    has_discount=has_discount,
                    url=None  # URL not available in Excel
                )
                
                db.session.add(cp)
                competitor_count += 1
            
            product.competitor_count = competitor_count
            
            products_data.append({
                'product': product,
                'competitor_count': competitor_count
            })
        
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue
    
    db.session.commit()
    
    return products_data

def _determine_brand(model, name):
    """
    Determine product brand from model or name
    
    Args:
        model: Product model
        name: Product name
    
    Returns:
        str: Brand name
    """
    text = f"{model} {name}".lower()
    
    if 'delonghi' in text or 'de longhi' in text:
        return 'DeLonghi'
    elif 'melitta' in text:
        return 'Melitta'
    elif 'nivona' in text:
        return 'Nivona'
    else:
        return 'Unknown'

def _calculate_statistics(products_data, upload_id):
    """
    Calculate statistics for upload
    
    Args:
        products_data: list of products with data
        upload_id: Upload ID
    
    Returns:
        dict: statistics
    """
    total_products = len(products_data)
    
    if total_products == 0:
        return {}
    
    # Calculate totals
    total_value = sum(p['product'].our_price * p['product'].quantity for p in products_data)
    avg_price = sum(p['product'].our_price for p in products_data) / total_products
    
    prices = [p['product'].our_price for p in products_data]
    min_price = min(prices)
    max_price = max(prices)
    
    # Count products by competitor count
    products_with_1_plus = sum(1 for p in products_data if p['competitor_count'] >= 1)
    products_with_2_plus = sum(1 for p in products_data if p['competitor_count'] >= 2)
    products_with_3_plus = sum(1 for p in products_data if p['competitor_count'] >= 3)
    
    # Count cheaper/more expensive products
    products_cheaper = 0
    products_expensive = 0
    products_no_competitors = 0
    
    for p_data in products_data:
        product = p_data['product']
        competitors = CompetitorPrice.query.filter_by(product_id=product.id).all()
        
        if len(competitors) == 0:
            products_no_competitors += 1
            continue
        
        # Check if our price is cheaper than any competitor
        is_cheaper = any(product.our_price < cp.price for cp in competitors)
        is_expensive = any(product.our_price > cp.price for cp in competitors)
        
        if is_cheaper:
            products_cheaper += 1
        if is_expensive:
            products_expensive += 1
    
    # Create statistic record
    statistic = Statistic(
        upload_id=upload_id,
        total_products=total_products,
        total_quantity=sum(p['product'].quantity for p in products_data),
        total_value=total_value,
        avg_our_price=avg_price,
        min_our_price=min_price,
        max_our_price=max_price,
        avg_competitors_per_product=sum(p['competitor_count'] for p in products_data) / total_products,
        products_with_1_plus_competitors=products_with_1_plus,
        products_with_2_plus_competitors=products_with_2_plus,
        products_with_3_plus_competitors=products_with_3_plus
    )
    
    db.session.add(statistic)
    db.session.commit()
    
    return {
        'total_products': total_products,
        'total_value': float(total_value),
        'avg_price': float(avg_price),
        'products_cheaper': products_cheaper,
        'products_expensive': products_expensive,
        'products_no_competitors': products_no_competitors
    }

