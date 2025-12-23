#!/usr/bin/env python3
"""
Test Veli Store scraper WITH Google Search enabled
Tests finding missing products that are not in category pages
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from scrapers.veli_store.veli_store_bs4_scraper import VeliStoreScraper

def test_with_google():
    """Test Veli Store scraping WITH Google Search for missing products"""
    
    print("=" * 80)
    print("TESTING VELI STORE SCRAPER WITH GOOGLE SEARCH")
    print("=" * 80)
    
    # Sample inventory models (from user's examples)
    # These should NOT be in coffee-makers category
    test_inventory_models = [
        # In category (should be found without Google)
        "ECAM22.110.SB",        # Coffee machine
        "E957-203",             # Melitta
        
        # NOT in category (need Google search)
        "CTJ2103.BK",           # Toaster - user example
        "CTOV2103.BG",          # Toaster - user example  
        "DLSC301",              # Accessory - user example
        "ECAM290.42.TB",        # Coffee machine - user example
    ]
    
    print(f"\nTest inventory models: {len(test_inventory_models)}")
    for model in test_inventory_models:
        print(f"  - {model}")
    
    print("\n" + "=" * 80)
    print("STEP 1: SCRAPING CATEGORY (no Google)")
    print("=" * 80)
    
    # First, scrape WITHOUT Google to see what we get
    scraper1 = VeliStoreScraper(enable_google_search=False)
    scraper1.setup_driver()
    
    try:
        products_from_category = scraper1.scrape_all_pages()
        print(f"\nFound in category: {len(products_from_category)} products")
        
        # Check which models we found
        found_models = set()
        for p in products_from_category:
            model = scraper1.extract_model_from_name(p['name'])
            if model:
                found_models.add(model.upper())
        
        print(f"Models found: {found_models}")
        
    finally:
        scraper1.driver.quit()
    
    print("\n" + "=" * 80)
    print("CHECKING: Which models are MISSING?")
    print("=" * 80)
    
    # Normalize test models for comparison
    test_models_normalized = {m.upper().replace('.', '').replace('-', '').replace(' ', '') for m in test_inventory_models}
    found_models_normalized = {m.upper().replace('.', '').replace('-', '').replace(' ', '') for m in found_models}
    
    # Find which test models are missing
    missing_test_models = []
    for test_model in test_inventory_models:
        test_clean = test_model.upper().replace('.', '').replace('-', '').replace(' ', '')
        is_found = any(test_clean in fm or fm in test_clean for fm in found_models_normalized)
        if is_found:
            print(f"  [FOUND in category] {test_model}")
        else:
            print(f"  [MISSING - need Google] {test_model}")
            missing_test_models.append(test_model)
    
    print(f"\nSummary:")
    print(f"  Found in category: {len(test_inventory_models) - len(missing_test_models)}")
    print(f"  Need Google search: {len(missing_test_models)}")
    
    if not missing_test_models:
        print("\n✓ All test models found in category - Google search not needed!")
        return
    
    print("\n" + "=" * 80)
    print("STEP 2: SCRAPING WITH GOOGLE SEARCH")
    print("=" * 80)
    print(f"\nNOTE: Will search Google ONLY for {len(missing_test_models)} missing models")
    print("      (Already found models are EXCLUDED)")
    print("      Time: ~3-5 seconds per missing product")
    print(f"      Estimated: ~{len(missing_test_models) * 4} seconds\n")
    
    input("Press ENTER to continue with Google search (or Ctrl+C to cancel)...")
    
    # Now scrape WITH Google search
    scraper2 = VeliStoreScraper(
        enable_google_search=True,
        inventory_models=test_inventory_models
    )
    scraper2.setup_driver()
    
    try:
        all_products = scraper2.scrape_all_pages()
        
        print("\n" + "=" * 80)
        print("FINAL RESULTS")
        print("=" * 80)
        print(f"Total products: {len(all_products)}")
        print(f"  From category: {len(products_from_category)}")
        print(f"  From Google: {len(all_products) - len(products_from_category)}")
        
        print("\nAll found products:")
        for i, p in enumerate(all_products, 1):
            model = scraper2.extract_model_from_name(p['name'])
            discount_info = f" (was {p['regular_price']})" if p['has_discount'] else ""
            print(f"{i:2d}. [{model:15s}] {p['name'][:45]:45s} {p['price']:8.2f}{discount_info}")
        
        # Check which test models we found
        found_test_models = set()
        for p in all_products:
            model = scraper2.extract_model_from_name(p['name'])
            if model:
                model_upper = model.upper().replace('.', '').replace('-', '')
                # Check if it matches any test model
                for test_model in test_inventory_models:
                    test_clean = test_model.upper().replace('.', '').replace('-', '')
                    if test_clean in model_upper or model_upper in test_clean:
                        found_test_models.add(test_model)
                        break
        
        print("\n" + "=" * 80)
        print("TEST MODELS FOUND:")
        print("=" * 80)
        for model in test_inventory_models:
            status = "[FOUND]" if model in found_test_models else "[NOT FOUND]"
            print(f"  {status} {model}")
        
        print(f"\nSuccess rate: {len(found_test_models)}/{len(test_inventory_models)} ({len(found_test_models)*100//len(test_inventory_models)}%)")
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Test stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper2.driver:
            scraper2.driver.quit()
        print("\nDone!")

if __name__ == "__main__":
    test_with_google()

