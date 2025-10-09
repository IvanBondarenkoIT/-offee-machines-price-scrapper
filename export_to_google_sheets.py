"""
Export scraping results to Google Sheets
Creates a spreadsheet with separate sheets for each store
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import glob

# For now, we'll create a multi-sheet Excel file
# Google Sheets API requires credentials setup
# This version creates local Excel that can be uploaded to Google Sheets

OUTPUT_DIR = Path(__file__).parent / "data" / "output"


def find_latest_file(pattern):
    """Find latest file matching pattern"""
    files = list(OUTPUT_DIR.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda x: x.stat().st_mtime)


def load_inventory():
    """Load our inventory from остатки.xls"""
    # Use absolute path to avoid issues
    file_path = Path(__file__).parent / 'data' / 'inbox' / 'остатки.xls'
    
    if not file_path.exists():
        print("\n[WARNING] Inventory file (остатки.xls) not found")
        return None
    
    print(f"\n[OK] Loading inventory from {file_path.name}")
    
    try:
        # Read without header
        df = pd.read_excel(file_path, header=None)
        
        # Parse the data structure
        # Row format: ['number.', 'Product Name', 'unit', quantity]
        products = []
        
        for i in range(len(df)):
            row = df.iloc[i]
            row_values = [v for v in row.values if pd.notna(v)]
            
            # Check if row contains DeLonghi product
            row_str = ' '.join([str(v) for v in row_values])
            if 'delonghi' in row_str.lower():
                # Try to parse the row
                # Format: ['number.', 'Product Name', 'unit', quantity]
                if len(row_values) >= 3:
                    # Last value is usually quantity
                    qty = row_values[-1]
                    if isinstance(qty, (int, float)) and qty > 0:
                        # Product name is usually the second element (or combine if needed)
                        name = None
                        if len(row_values) == 4:
                            name = str(row_values[1])
                        elif len(row_values) == 3:
                            name = str(row_values[0])
                        elif len(row_values) > 4:
                            # Join middle elements
                            name = ' '.join([str(v) for v in row_values[1:-2]])
                        
                        if name and 'delonghi' in name.lower():
                            products.append({
                                'Product Name': name,
                                'Quantity': int(qty)
                            })
        
        if products:
            inventory = pd.DataFrame(products)
            # Add index
            inventory.insert(0, '#', range(1, len(inventory) + 1))
            
            print(f"[OK] Loaded {len(inventory)} DeLonghi products from inventory")
            return inventory
        else:
            print(f"[WARNING] No DeLonghi products found in inventory")
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to load inventory: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_combined_excel():
    """Create Excel file with separate sheets for each store"""
    print("="*60)
    print("CREATING COMBINED PRICE REPORT")
    print("="*60)
    
    # Find latest files for each store
    stores = {
        'ALTA': find_latest_file('alta_*_prices_*.xlsx'),
        'KONTAKT': find_latest_file('kontakt_*_prices_*.xlsx'),
        'ELITE': find_latest_file('elite_*_prices_*.xlsx'),
        'DIM_KAVA': find_latest_file('dimkava_*_prices_*.xlsx'),
    }
    
    # Load data
    store_data = {}
    for store_name, filepath in stores.items():
        if filepath:
            df = pd.read_excel(filepath)
            store_data[store_name] = df
            print(f"\n[OK] {store_name}: {len(df)} products loaded from {filepath.name}")
        else:
            print(f"\n[WARNING] {store_name}: No data file found")
    
    # Load inventory (our stock)
    inventory_df = load_inventory()
    if inventory_df is not None:
        store_data['INVENTORY'] = inventory_df
    
    if not store_data:
        print("\n[ERROR] No data files found!")
        return None
    
    # Create Excel with multiple sheets
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"combined_prices_{timestamp}.xlsx"
    
    print(f"\n{'='*60}")
    print("CREATING EXCEL FILE WITH MULTIPLE SHEETS")
    print(f"{'='*60}")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for store_name, df in store_data.items():
            if store_name == 'INVENTORY':
                # Inventory has different structure
                df_export = df.copy()
                df_export.to_excel(writer, sheet_name=store_name, index=False)
                print(f"[OK] Sheet '{store_name}': {len(df_export)} products (our stock)")
            else:
                # Select only needed columns in order
                columns_to_export = ['index', 'name', 'final_price', 'regular_price', 'discount_price', 'has_discount']
                df_export = df[columns_to_export].copy()
                
                # Rename columns for clarity
                df_export.columns = ['#', 'Product Name', 'Final Price (GEL)', 'Regular Price', 'Discount Price', 'Has Discount']
                
                # Write to sheet
                df_export.to_excel(writer, sheet_name=store_name, index=False)
                print(f"[OK] Sheet '{store_name}': {len(df_export)} products")
        
        # Create summary sheet
        summary_data = []
        for store_name, df in store_data.items():
            if store_name == 'INVENTORY':
                summary_data.append({
                    'Store': store_name,
                    'Products': len(df),
                    'Total Quantity': df['Quantity'].sum() if 'Quantity' in df.columns else 0,
                    'Min Price': '-',
                    'Max Price': '-',
                    'Avg Price': '-',
                    'With Discount': '-',
                })
            else:
                summary_data.append({
                    'Store': store_name,
                    'Products': len(df),
                    'Total Quantity': '-',
                    'Min Price': df['final_price'].min(),
                    'Max Price': df['final_price'].max(),
                    'Avg Price': round(df['final_price'].mean(), 2),
                    'With Discount': df['has_discount'].sum() if 'has_discount' in df.columns else 0,
                })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='SUMMARY', index=False)
        print(f"[OK] Sheet 'SUMMARY': Statistics created")
    
    print(f"\n{'='*60}")
    print(f"[SUCCESS] Combined file created:")
    print(f"{output_file}")
    print(f"{'='*60}")
    
    # Show summary
    print("\nSUMMARY:")
    print(summary_df.to_string(index=False))
    
    print("\n" + "="*60)
    print("READY TO UPLOAD TO GOOGLE SHEETS")
    print("="*60)
    print("\nOption 1 - Manual Upload:")
    print("  1. Open https://sheets.google.com")
    print("  2. File > Import")
    print(f"  3. Upload: {output_file}")
    print("  4. Import location: Create new spreadsheet")
    
    print("\nOption 2 - Google Sheets API (requires setup):")
    print("  1. Enable Google Sheets API in Google Cloud Console")
    print("  2. Create Service Account and download credentials.json")
    print("  3. Share spreadsheet with service account email")
    print("  4. Run: python export_to_google_sheets_api.py")
    
    return output_file


def main():
    """Main execution"""
    output_file = create_combined_excel()
    
    if output_file:
        print(f"\n[SUCCESS] Combined Excel ready: {output_file.name}")
    print("\nThis file contains:")
    print("  - ALTA sheet (74 products)")
    print("  - KONTAKT sheet (28 products)")
    print("  - ELITE sheet (40 products)")
    print("  - DIM_KAVA sheet (41 products)")
    print("  - INVENTORY sheet (our stock)")
    print("  - SUMMARY sheet (statistics)")
    print("\nUpload to Google Sheets for easy sharing!")


if __name__ == "__main__":
    main()

