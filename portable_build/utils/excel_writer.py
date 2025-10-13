"""
Excel writer utility
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from config import OUTPUT_DIR, OUTPUT_CONFIG


def save_to_excel(data: List[Dict], filename: str = None) -> Path:
    """
    Save scraped data to Excel file
    
    Args:
        data: List of dictionaries with product data
        filename: Optional custom filename
        
    Returns:
        Path to the saved file
    """
    if not data:
        raise ValueError("No data to save")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Generate filename with timestamp if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = OUTPUT_CONFIG["excel_filename"].format(timestamp=timestamp)
    
    # Full path
    filepath = OUTPUT_DIR / filename
    
    # Save to Excel
    df.to_excel(filepath, index=False, engine='openpyxl')
    
    return filepath


def save_to_csv(data: List[Dict], filename: str = None) -> Path:
    """
    Save scraped data to CSV file
    
    Args:
        data: List of dictionaries with product data
        filename: Optional custom filename
        
    Returns:
        Path to the saved file
    """
    if not data:
        raise ValueError("No data to save")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Generate filename with timestamp if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = OUTPUT_CONFIG["csv_filename"].format(timestamp=timestamp)
    
    # Full path
    filepath = OUTPUT_DIR / filename
    
    # Save to CSV
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    return filepath

