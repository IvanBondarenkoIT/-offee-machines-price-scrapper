"""
Data formatting utilities
"""
from datetime import datetime, date

def format_price(price):
    """
    Format price for display
    
    Args:
        price: Numeric price value
    
    Returns:
        str: Formatted price (e.g., "1,234.56")
    """
    if price is None:
        return '-'
    
    return f"{float(price):,.2f}"

def format_date(date_value):
    """
    Format date for display
    
    Args:
        date_value: date or datetime object
    
    Returns:
        str: Formatted date (e.g., "2025-10-28")
    """
    if date_value is None:
        return '-'
    
    if isinstance(date_value, datetime):
        return date_value.strftime('%Y-%m-%d')
    elif isinstance(date_value, date):
        return date_value.strftime('%Y-%m-%d')
    
    return str(date_value)

def format_datetime(datetime_value):
    """
    Format datetime for display
    
    Args:
        datetime_value: datetime object
    
    Returns:
        str: Formatted datetime (e.g., "2025-10-28 14:30")
    """
    if datetime_value is None:
        return '-'
    
    return datetime_value.strftime('%Y-%m-%d %H:%M')

def format_percentage(value, total):
    """
    Calculate and format percentage
    
    Args:
        value: Part value
        total: Total value
    
    Returns:
        str: Formatted percentage (e.g., "45.2%")
    """
    if total == 0:
        return '0%'
    
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"

def price_difference(our_price, competitor_price):
    """
    Calculate price difference
    
    Args:
        our_price: Our price
        competitor_price: Competitor price
    
    Returns:
        dict: {
            'amount': difference amount,
            'percentage': difference percentage,
            'status': 'cheaper' or 'more_expensive' or 'equal'
        }
    """
    if our_price is None or competitor_price is None:
        return {
            'amount': 0,
            'percentage': 0,
            'status': 'unknown'
        }
    
    our_price = float(our_price)
    competitor_price = float(competitor_price)
    
    diff = our_price - competitor_price
    
    if diff == 0:
        status = 'equal'
    elif diff < 0:
        status = 'cheaper'
    else:
        status = 'more_expensive'
    
    percentage = 0
    if competitor_price != 0:
        percentage = (diff / competitor_price) * 100
    
    return {
        'amount': abs(diff),
        'percentage': abs(percentage),
        'status': status
    }

def format_competitor_price(competitor_price):
    """
    Format competitor price with discount information
    
    Args:
        competitor_price: CompetitorPrice object
    
    Returns:
        str: Formatted price string
    """
    if competitor_price.has_discount and competitor_price.discount_price:
        return f"{format_price(competitor_price.regular_price)} → {format_price(competitor_price.discount_price)}"
    else:
        return format_price(competitor_price.price)

