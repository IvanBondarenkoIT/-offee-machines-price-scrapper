"""
Price Analysis Script
Analyze and compare scraped prices with reference prices
"""
import pandas as pd
import glob
from pathlib import Path
from datetime import datetime

# Directories
OUTPUT_DIR = Path("data/output")
INBOX_DIR = Path("data/inbox")

def find_latest_scrape(pattern="alta_delonghi_prices_*.xlsx"):
    """Find the latest scraped file"""
    files = list(OUTPUT_DIR.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda x: x.stat().st_mtime)

def load_scraped_data(filepath):
    """Load scraped data from Excel"""
    df = pd.read_excel(filepath)
    print(f"\n[OK] Loaded scraped data: {filepath.name}")
    print(f"  Total products: {len(df)}")
    return df

def analyze_prices(df):
    """Analyze price statistics"""
    print("\n" + "="*60)
    print("PRICE ANALYSIS")
    print("="*60)
    
    # Basic stats
    print(f"\nTotal products: {len(df)}")
    print(f"Products with discount: {df['has_discount'].sum()}")
    print(f"Discount rate: {df['has_discount'].sum() / len(df) * 100:.1f}%")
    
    # Price statistics
    print(f"\nPrice Statistics (GEL):")
    print(f"  Min price: {df['final_price'].min():.2f}")
    print(f"  Max price: {df['final_price'].max():.2f}")
    print(f"  Average price: {df['final_price'].mean():.2f}")
    print(f"  Median price: {df['final_price'].median():.2f}")
    
    # Discount statistics
    discounted = df[df['has_discount'] == True]
    if len(discounted) > 0:
        discounted['discount_amount'] = discounted['regular_price'] - discounted['discount_price']
        discounted['discount_percent'] = (discounted['discount_amount'] / discounted['regular_price'] * 100)
        
        print(f"\nDiscount Statistics:")
        print(f"  Average discount: {discounted['discount_amount'].mean():.2f} GEL")
        print(f"  Average discount %: {discounted['discount_percent'].mean():.1f}%")
        print(f"  Max discount: {discounted['discount_amount'].max():.2f} GEL")
        print(f"  Max discount %: {discounted['discount_percent'].max():.1f}%")
    
    return df

def top_products(df, n=10):
    """Show top N products by price"""
    print(f"\nTop {n} Most Expensive Products:")
    top = df.nlargest(n, 'final_price')[['name', 'final_price', 'has_discount']]
    for idx, row in top.iterrows():
        discount_mark = "[DISC]" if row['has_discount'] else "      "
        print(f"  {discount_mark} {row['final_price']:>7.2f} GEL - {row['name']}")
    
    print(f"\nTop {n} Cheapest Products:")
    bottom = df.nsmallest(n, 'final_price')[['name', 'final_price', 'has_discount']]
    for idx, row in bottom.iterrows():
        discount_mark = "[DISC]" if row['has_discount'] else "      "
        print(f"  {discount_mark} {row['final_price']:>7.2f} GEL - {row['name']}")

def price_distribution(df):
    """Show price distribution"""
    print("\nPrice Distribution:")
    bins = [0, 100, 500, 1000, 2000, 3000, 10000]
    labels = ["0-100", "100-500", "500-1000", "1000-2000", "2000-3000", "3000+"]
    
    df['price_range'] = pd.cut(df['final_price'], bins=bins, labels=labels)
    distribution = df['price_range'].value_counts().sort_index()
    
    for range_label, count in distribution.items():
        bar = "#" * int(count / len(df) * 50)
        print(f"  {range_label:>12} GEL: {bar} {count:>2} ({count/len(df)*100:.1f}%)")

def main():
    """Main execution"""
    print("="*60)
    print("COFFEE MACHINES PRICE ANALYSIS")
    print("="*60)
    
    # Find latest scraped file
    latest_file = find_latest_scrape()
    if not latest_file:
        print("\n[ERROR] No scraped files found in data/output/")
        print("   Please run the scraper first: python main.py")
        return
    
    # Load and analyze
    df = load_scraped_data(latest_file)
    df = analyze_prices(df)
    top_products(df, n=10)
    price_distribution(df)
    
    # Save analysis report
    report_file = OUTPUT_DIR / f"price_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    print(f"\n[INFO] Analysis report would be saved to: {report_file}")
    
    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)

if __name__ == "__main__":
    main()

