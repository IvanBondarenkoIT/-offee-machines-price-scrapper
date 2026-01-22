"""
Export WooCommerce stock data to Excel
Standalone script for exporting product data from WooCommerce API
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from utils.woocommerce_client import WooCommerceClient, get_woocommerce_config


def export_woocommerce_data(output_dir: Path = None) -> Path:
    """
    Export WooCommerce stock data to Excel file
    
    Args:
        output_dir: Directory to save the file (default: data/output)
        
    Returns:
        Path to the created Excel file
    """
    print("="*80)
    print("WOOCOMMERCE DATA EXPORT")
    print("="*80)
    
    # Get configuration
    config = get_woocommerce_config()
    if not config:
        print("[ERROR] WooCommerce configuration not found")
        print("  Please set environment variables:")
        print("    WC_URL")
        print("    WC_CONSUMER_KEY")
        print("    WC_CONSUMER_SECRET")
        return None
    
    # Set output directory
    if output_dir is None:
        base_dir = Path(__file__).parent
        output_dir = base_dir / 'data' / 'output'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create client and get data
    print("\n[1/3] Connecting to WooCommerce API...")
    client = WooCommerceClient(**config)
    
    print("[2/3] Fetching product data...")
    df = client.get_stock_data()
    
    if df is None or len(df) == 0:
        print("[ERROR] No data retrieved from WooCommerce")
        return None
    
    print(f"[OK] Retrieved {len(df)} products")
    
    # Prepare data for export
    print("[3/3] Preparing export data...")
    
    # Select and rename columns for export
    export_data = []
    for idx, row in df.iterrows():
        # Format price (handle regular and sale prices)
        price_str = "-"
        if pd.notna(row.get('price')):
            try:
                price = float(row['price']) if pd.notna(row.get('price')) else None
                regular_price = float(row.get('regular_price')) if pd.notna(row.get('regular_price')) else None
                sale_price = float(row.get('sale_price')) if pd.notna(row.get('sale_price')) else None
                
                if sale_price and sale_price != price and price is not None:
                    # Has discount
                    if regular_price:
                        price_str = f"{regular_price:.2f} \\ {sale_price:.2f}"
                    else:
                        price_str = f"{price:.2f} \\ {sale_price:.2f}"
                elif price is not None:
                    # Regular price
                    price_str = f"{price:.2f}"
            except (ValueError, TypeError):
                # Fallback to string representation
                price_str = str(row.get('price', '-'))
        
        export_data.append({
            'Model': row['model'],
            'Name': row['name'],
            'Price (GEL)': price_str,
            'Stock': int(row['stock_quantity']) if pd.notna(row['stock_quantity']) else 0,
            'URL': row['url'],
            'SKU': row.get('sku', ''),
            'Regular Price': row.get('regular_price', '') if pd.notna(row.get('regular_price')) else '',
            'Sale Price': row.get('sale_price', '') if pd.notna(row.get('sale_price')) else '',
        })
    
    # Create DataFrame
    export_df = pd.DataFrame(export_data)
    
    # Sort by model
    export_df = export_df.sort_values('Model')
    
    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'woocommerce_export_{timestamp}.xlsx'
    filepath = output_dir / filename
    
    # Save to Excel
    print(f"\nSaving to: {filepath}")
    export_df.to_excel(filepath, index=False, engine='openpyxl')
    
    print(f"[OK] Export complete!")
    print(f"  File: {filename}")
    print(f"  Products: {len(export_df)}")
    print(f"  Location: {filepath}")
    
    # Print summary
    print("\n" + "="*80)
    print("EXPORT SUMMARY")
    print("="*80)
    print(f"Total products: {len(export_df)}")
    print(f"Products with stock: {(export_df['Stock'] > 0).sum()}")
    print(f"Total stock quantity: {export_df['Stock'].sum()}")
    print(f"Products with prices: {(export_df['Price (GEL)'] != '-').sum()}")
    print("="*80)
    
    return filepath


if __name__ == "__main__":
    try:
        filepath = export_woocommerce_data()
        if filepath:
            print(f"\n[SUCCESS] Export completed: {filepath}")
        else:
            print("\n[FAILED] Export failed")
            exit(1)
    except Exception as e:
        print(f"\n[ERROR] Export failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
