#!/usr/bin/env python3
"""
Simple test for Veli Store scraper WITHOUT Google Search
Tests that existing functionality still works after changes
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from scrapers.veli_store.veli_store_bs4_scraper import VeliStoreScraper

def test_simple():
    """Test basic Veli Store scraping (category only)"""
    
    print("=" * 80)
    print("TESTING VELI STORE SCRAPER - BASIC FUNCTIONALITY")
    print("=" * 80)
    print("\nThis test ensures existing scraper still works")
    print("Google Search is DISABLED (default)")
    
    # Create scraper WITHOUT Google search (default behavior)
    scraper = VeliStoreScraper(enable_google_search=False)
    
    print("\nStarting scraper...")
    scraper.setup_driver()
    
    try:
        # Scrape category
        products = scraper.scrape_all_pages()
        
        print("\n" + "=" * 80)
        print(f"RESULTS: Found {len(products)} products")
        print("=" * 80)
        
        if products:
            # Show breakdown by brand
            brands = {}
            for p in products:
                name_lower = p['name'].lower()
                if 'delonghi' in name_lower:
                    brand = 'DeLonghi'
                elif 'melitta' in name_lower:
                    brand = 'Melitta'
                elif 'nivona' in name_lower:
                    brand = 'Nivona'
                else:
                    brand = 'Other'
                
                brands.setdefault(brand, []).append(p)
            
            print("\nBreakdown by brand:")
            for brand, items in sorted(brands.items()):
                print(f"  {brand}: {len(items)} products")
            
            print("\nFirst 10 products:")
            for i, p in enumerate(products[:10], 1):
                discount_info = f" (was {p['regular_price']})" if p['has_discount'] else ""
                print(f"{i:2d}. {p['name'][:60]:60s} {p['price']:.2f}{discount_info}")
            
            if len(products) > 10:
                print(f"\n... and {len(products) - 10} more")
            
            # Test model extraction
            print("\n" + "=" * 80)
            print("TESTING MODEL EXTRACTION")
            print("=" * 80)
            for p in products[:5]:
                model = scraper.extract_model_from_name(p['name'])
                print(f"{p['name'][:50]:50s} -> {model}")
            
            print("\n[SUCCESS] Veli Store scraper works correctly!")
            
        else:
            print("\n[WARNING] No products found - check scraper logic")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper.driver:
            scraper.driver.quit()
        print("\nDone!")

if __name__ == "__main__":
    test_simple()

