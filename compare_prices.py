"""
Compare scraped prices with our inventory
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))
from utils.product_matcher import extract_model, models_match, fuzzy_match


# Directories
OUTPUT_DIR = Path("data/output")
INBOX_DIR = Path("data/inbox")


def find_latest_scrape(pattern="alta_delonghi_prices_*.xlsx"):
    """Find the latest scraped file"""
    files = list(OUTPUT_DIR.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda x: x.stat().st_mtime)


def load_our_inventory():
    """Load our inventory from comparison file"""
    # Try to find the comparison file
    comparison_files = list(INBOX_DIR.glob("*.xlsx"))
    comparison_files = [f for f in comparison_files if "сравн" in f.name.lower() or "сравнение" in f.name.lower()]
    
    # Filter out temp files
    comparison_files = [f for f in comparison_files if not f.name.startswith('~$')]
    
    if not comparison_files:
        print("[WARNING] Comparison file not found in data/inbox/")
        return None
    
    comparison_file = comparison_files[0]
    print(f"\n[OK] Loading our inventory: {comparison_file.name}")
    
    try:
        df = pd.read_excel(comparison_file)
        
        # Skip header rows and set proper column names
        # Row 1 contains "Название" and shop names
        df.columns = ['Qty', 'Model', 'Our_Price', 'Shop1', 'Shop2', 'Shop3', 'Shop4', 'Shop5']
        
        # Skip first 2 rows (headers)
        df = df.iloc[2:].reset_index(drop=True)
        
        # Remove rows where Model is NaN
        df = df[df['Model'].notna()]
        
        print(f"  Total products in inventory: {len(df)}")
        print(f"  First few models: {df['Model'].head(3).tolist()}")
        return df
    except Exception as e:
        print(f"[ERROR] Failed to load comparison file: {e}")
        import traceback
        traceback.print_exc()
        return None


def extract_models_from_scraped(df):
    """Extract models from scraped data"""
    print("\n[INFO] Extracting models from scraped data...")
    df['model'] = df['name'].apply(extract_model)
    
    with_model = df[df['model'].notna()]
    without_model = df[df['model'].isna()]
    
    print(f"  Products with model: {len(with_model)}")
    print(f"  Products without model: {len(without_model)}")
    
    if len(without_model) > 0:
        print("\n  Products without detected model:")
        for idx, row in without_model.iterrows():
            print(f"    - {row['name']}")
    
    return df


def compare_with_inventory(scraped_df, inventory_df):
    """Compare scraped prices with our inventory"""
    print("\n" + "="*80)
    print("PRICE COMPARISON")
    print("="*80)
    
    # Extract models from scraped data
    scraped_df = extract_models_from_scraped(scraped_df)
    
    # Use predefined column names
    model_col = 'Model'
    price_col = 'Our_Price'
    
    print(f"\n[INFO] Using column '{model_col}' for models")
    print(f"[INFO] Using column '{price_col}' for our prices")
    
    # Match products
    matches = []
    
    for idx, scraped_row in scraped_df.iterrows():
        if pd.isna(scraped_row['model']):
            continue
        
        scraped_model = scraped_row['model']
        
        # Try to find in inventory
        for inv_idx, inv_row in inventory_df.iterrows():
            if pd.isna(inv_row[model_col]):
                continue
            
            inv_model = str(inv_row[model_col])
            
            if models_match(scraped_model, inv_model):
                match_type = "exact"
            elif fuzzy_match(scraped_model, inv_model):
                match_type = "fuzzy"
            else:
                continue
            
            # Found a match!
            our_price = inv_row[price_col] if price_col and not pd.isna(inv_row[price_col]) else None
            alta_price = scraped_row['final_price']
            
            price_diff = None
            price_diff_pct = None
            if our_price and alta_price:
                price_diff = our_price - alta_price
                price_diff_pct = (price_diff / alta_price) * 100
            
            matches.append({
                'model': scraped_model,
                'product_name': scraped_row['name'],
                'alta_price': alta_price,
                'alta_regular': scraped_row['regular_price'],
                'alta_discount': scraped_row['discount_price'],
                'our_price': our_price,
                'price_diff': price_diff,
                'price_diff_pct': price_diff_pct,
                'match_type': match_type,
            })
            break  # Found match, no need to continue
    
    if not matches:
        print("\n[WARNING] No matching products found!")
        print("\nPossible reasons:")
        print("  - Model codes don't match")
        print("  - Different naming conventions")
        print("  - Products not in our inventory")
        return
    
    # Create DataFrame
    matches_df = pd.DataFrame(matches)
    
    print(f"\n[OK] Found {len(matches)} matching products")
    print(f"  Exact matches: {len(matches_df[matches_df['match_type'] == 'exact'])}")
    print(f"  Fuzzy matches: {len(matches_df[matches_df['match_type'] == 'fuzzy'])}")
    
    # Show comparison
    print("\n" + "="*80)
    print("MATCHED PRODUCTS")
    print("="*80)
    
    for idx, row in matches_df.iterrows():
        print(f"\n[{row['model']}] {row['product_name']}")
        print(f"  ALTA price:  {row['alta_price']:>7.2f} GEL", end="")
        if row['alta_discount']:
            print(f" (was {row['alta_regular']:.2f})")
        else:
            print()
        
        if row['our_price']:
            print(f"  Our price:   {row['our_price']:>7.2f} GEL")
            if row['price_diff']:
                sign = "+" if row['price_diff'] > 0 else ""
                print(f"  Difference:  {sign}{row['price_diff']:>7.2f} GEL ({sign}{row['price_diff_pct']:.1f}%)")
                
                if row['price_diff'] > 0:
                    print(f"  Status: [!] We are MORE expensive by {row['price_diff']:.2f} GEL")
                elif row['price_diff'] < 0:
                    print(f"  Status: [OK] We are CHEAPER by {abs(row['price_diff']):.2f} GEL")
                else:
                    print(f"  Status: [=] Same price")
    
    # Summary statistics
    if len(matches_df[matches_df['our_price'].notna()]) > 0:
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        with_prices = matches_df[matches_df['our_price'].notna()]
        
        cheaper_count = len(with_prices[with_prices['price_diff'] < 0])
        same_count = len(with_prices[with_prices['price_diff'] == 0])
        expensive_count = len(with_prices[with_prices['price_diff'] > 0])
        
        print(f"\nWe are CHEAPER:       {cheaper_count:>2} products")
        print(f"We have SAME price:   {same_count:>2} products")
        print(f"We are MORE expensive: {expensive_count:>2} products")
        
        if len(with_prices) > 0:
            avg_diff = with_prices['price_diff'].mean()
            print(f"\nAverage price difference: {avg_diff:+.2f} GEL")
    
    # Save report
    report_file = OUTPUT_DIR / f"price_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    matches_df.to_excel(report_file, index=False)
    print(f"\n[OK] Comparison saved to: {report_file}")
    
    return matches_df


def main():
    """Main execution"""
    print("="*80)
    print("PRICE COMPARISON: ALTA vs OUR INVENTORY")
    print("="*80)
    
    # Load latest scrape
    latest_file = find_latest_scrape()
    if not latest_file:
        print("\n[ERROR] No scraped files found!")
        print("Please run the scraper first: python main.py")
        return
    
    print(f"\n[OK] Loading scraped data: {latest_file.name}")
    scraped_df = pd.read_excel(latest_file)
    print(f"  Total products scraped: {len(scraped_df)}")
    
    # Load our inventory
    inventory_df = load_our_inventory()
    if inventory_df is None:
        print("\n[ERROR] Could not load inventory for comparison")
        return
    
    # Compare
    compare_with_inventory(scraped_df, inventory_df)
    
    print("\n" + "="*80)
    print("Comparison complete!")
    print("="*80)


if __name__ == "__main__":
    main()

