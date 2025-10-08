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

OUTPUT_DIR = Path("data/output")


def find_latest_file(pattern):
    """Find latest file matching pattern"""
    files = list(OUTPUT_DIR.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda x: x.stat().st_mtime)


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
            summary_data.append({
                'Store': store_name,
                'Products': len(df),
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
        print("  - SUMMARY sheet (statistics)")
        print("\nUpload to Google Sheets for easy sharing!")


if __name__ == "__main__":
    main()

