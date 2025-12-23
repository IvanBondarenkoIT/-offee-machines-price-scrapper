#!/usr/bin/env python3
"""
Test Veli Store scraper with direct URLs
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from scrapers.veli_store.veli_store_bs4_scraper import VeliStoreScraper

def test_direct_urls():
    """Test scraping with direct URLs from config"""
    
    print("=" * 80)
    print("TESTING VELI STORE WITH DIRECT URLs")
    print("=" * 80)
    
    # Create scraper with direct URLs enabled (default)
    scraper = VeliStoreScraper(
        enable_google_search=False,  # Disable Google
        use_direct_urls=True         # Enable direct URLs (default)
    )
    
    print(f"\nDirect URLs loaded: {len(scraper.direct_urls)}")
    for model, info in scraper.direct_urls.items():
        print(f"  - {model}: {info['note']}")
    
    print("\n" + "=" * 80)
    print("SCRAPING...")
    print("=" * 80)
    
    scraper.setup_driver()
    
    try:
        products = scraper.scrape_all_pages()
        
        print("\n" + "=" * 80)
        print(f"RESULTS: {len(products)} products")
        print("=" * 80)
        
        # Breakdown
        from_category = 0
        from_direct = 0
        
        for p in products:
            # Check if from direct URLs
            is_direct = any(
                p['url'].startswith(info['url'].split('?')[0])
                for info in scraper.direct_urls.values()
            )
            if is_direct:
                from_direct += 1
            else:
                from_category += 1
        
        print(f"\nBreakdown:")
        print(f"  From category: {from_category}")
        print(f"  From direct URLs: {from_direct}")
        
        print(f"\nAll products:")
        for i, p in enumerate(products, 1):
            model = scraper.extract_model_from_name(p['name'])
            discount_info = f" (was {p['regular_price']})" if p['has_discount'] else ""
            source = "[DIRECT]" if any(p['url'].startswith(info['url'].split('?')[0]) for info in scraper.direct_urls.values()) else "[CATEGORY]"
            print(f"{i:2d}. {source:10s} [{model:15s}] {p['name'][:40]:40s} {p['price']:8.2f}{discount_info}")
        
        # Save
        scraper.save_to_excel(products)
        
        print("\n" + "=" * 80)
        print(f"SUCCESS! Total: {len(products)} products")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper.driver:
            scraper.driver.quit()
        print("\nDone!")

if __name__ == "__main__":
    test_direct_urls()

