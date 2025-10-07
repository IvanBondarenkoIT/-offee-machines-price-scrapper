"""
Product Matcher - Extract and match product models
"""
import re
from typing import Optional


def extract_model(product_name: str) -> Optional[str]:
    """
    Extract DeLonghi model from product name
    
    Examples:
        "DeLonghi Magnifica S (ECAM22.114.B)" -> "ECAM22.114.B"
        "DeLonghi ECAM22.114.B" -> "ECAM22.114.B"
        "DeLonghi Dinamica (ECAM350.55.B)" -> "ECAM350.55.B"
    
    Args:
        product_name: Full product name
        
    Returns:
        Model code or None if not found
    """
    if not product_name:
        return None
    
    # Pattern 1: Model in parentheses (ECAM22.114.B)
    pattern1 = r'\(([A-Z0-9]+[.\-][A-Z0-9.]+)\)'
    match = re.search(pattern1, product_name)
    if match:
        return match.group(1)
    
    # Pattern 2: Model after "DeLonghi" or at the end
    # Examples: ECAM22.114.B, EC685.R, DLSC310
    pattern2 = r'([A-Z]{2,}[0-9]+[.\-][A-Z0-9.]+[A-Z]?)'
    match = re.search(pattern2, product_name)
    if match:
        return match.group(1)
    
    # Pattern 3: Simple model codes like DLSC310, KG200
    pattern3 = r'\b([A-Z]{2,}[0-9]{3,})\b'
    match = re.search(pattern3, product_name)
    if match:
        return match.group(1)
    
    return None


def normalize_model(model: str) -> str:
    """
    Normalize model code for comparison
    Remove spaces, convert to uppercase
    
    Args:
        model: Model code
        
    Returns:
        Normalized model code
    """
    if not model:
        return ""
    
    # Remove spaces and convert to uppercase
    normalized = model.strip().upper()
    
    # Remove common prefixes/suffixes that don't affect the model
    normalized = normalized.replace("DELONGHI", "").strip()
    
    return normalized


def models_match(model1: str, model2: str) -> bool:
    """
    Check if two model codes match
    
    Args:
        model1: First model code
        model2: Second model code
        
    Returns:
        True if models match
    """
    if not model1 or not model2:
        return False
    
    norm1 = normalize_model(model1)
    norm2 = normalize_model(model2)
    
    return norm1 == norm2


def fuzzy_match(model1: str, model2: str) -> bool:
    """
    Fuzzy match - check if models are similar
    Useful for variants like ECAM22.114.B vs ECAM22.114.SB
    
    Args:
        model1: First model code
        model2: Second model code
        
    Returns:
        True if models are similar
    """
    if models_match(model1, model2):
        return True
    
    norm1 = normalize_model(model1)
    norm2 = normalize_model(model2)
    
    # Check if one is a substring of another (for color variants)
    # ECAM22.114 in both ECAM22.114.B and ECAM22.114.SB
    base1 = norm1.rsplit('.', 1)[0] if '.' in norm1 else norm1
    base2 = norm2.rsplit('.', 1)[0] if '.' in norm2 else norm2
    
    return base1 == base2

