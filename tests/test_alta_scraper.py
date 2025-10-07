"""
Tests for ALTA scraper
Quick smoke tests to verify scraper functionality
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.alta.alta_bs4_scraper import AltaBS4Scraper
from utils.product_matcher import extract_model, models_match, fuzzy_match
import time


def test_alta_bs4_scraper_quick():
    """
    Quick test: Load page, get at least 16 products
    Should complete in < 1 minute
    """
    print("\n" + "="*60)
    print("TEST: ALTA BS4 Scraper - Quick Test")
    print("="*60)
    
    start_time = time.time()
    scraper = AltaBS4Scraper()
    
    try:
        # Setup
        scraper.setup_driver()
        print("[OK] Driver setup successful")
        
        # Load page (don't click Load More - just initial load)
        scraper.driver.get(scraper.url)
        time.sleep(3)
        print("[OK] Page loaded")
        
        # Get HTML and parse
        html = scraper.get_page_html()
        print(f"[OK] Got HTML ({len(html)} chars)")
        
        # Parse
        scraper.parse_with_bs4(html)
        
        # Verify results
        assert len(scraper.products) >= 10, f"Expected at least 10 products, got {len(scraper.products)}"
        print(f"[OK] Found {len(scraper.products)} products")
        
        # Check data structure
        first_product = scraper.products[0]
        required_fields = ['index', 'name', 'final_price', 'scraped_at', 'url']
        for field in required_fields:
            assert field in first_product, f"Missing field: {field}"
        print("[OK] Data structure valid")
        
        # Check if products have names
        assert first_product['name'], "Product name is empty"
        assert len(first_product['name']) > 5, "Product name too short"
        print(f"[OK] Sample product: {first_product['name'][:50]}...")
        
        # Check if prices are numeric
        assert isinstance(first_product['final_price'], (int, float)), "Price is not numeric"
        assert first_product['final_price'] > 0, "Price is not positive"
        print(f"[OK] Sample price: {first_product['final_price']} GEL")
        
        elapsed = time.time() - start_time
        print(f"\n[SUCCESS] Quick test passed in {elapsed:.1f} seconds")
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        scraper.close()


def test_model_extraction():
    """Test product model extraction"""
    print("\n" + "="*60)
    print("TEST: Model Extraction")
    print("="*60)
    
    test_cases = [
        ("DeLonghi Magnifica S (ECAM22.114.B)", "ECAM22.114.B"),
        ("DeLonghi Dinamica (ECAM350.55.B)", "ECAM350.55.B"),
        ("DeLonghi EC685.R Dedica", "EC685.R"),
        ("DeLonghi ECAM22.114.B", "ECAM22.114.B"),
        ("DeLonghi Coffee Glasses (DLSC310)", "DLSC310"),
    ]
    
    passed = 0
    for product_name, expected_model in test_cases:
        extracted = extract_model(product_name)
        if extracted == expected_model:
            print(f"[OK] {product_name[:40]:40} -> {extracted}")
            passed += 1
        else:
            print(f"[FAIL] {product_name[:40]:40} -> {extracted} (expected {expected_model})")
    
    success_rate = passed / len(test_cases) * 100
    print(f"\n[RESULT] {passed}/{len(test_cases)} tests passed ({success_rate:.0f}%)")
    
    return passed == len(test_cases)


def test_model_matching():
    """Test model matching logic"""
    print("\n" + "="*60)
    print("TEST: Model Matching")
    print("="*60)
    
    # Exact matches
    assert models_match("ECAM22.114.B", "ECAM22.114.B"), "Exact match failed"
    print("[OK] Exact match: ECAM22.114.B")
    
    # Case insensitive
    assert models_match("ecam22.114.b", "ECAM22.114.B"), "Case insensitive match failed"
    print("[OK] Case insensitive: ecam22.114.b == ECAM22.114.B")
    
    # Fuzzy match (color variants)
    assert fuzzy_match("ECAM22.114.B", "ECAM22.114.SB"), "Fuzzy match failed for color variants"
    print("[OK] Fuzzy match: ECAM22.114.B ~ ECAM22.114.SB")
    
    # Should not match
    assert not models_match("ECAM22.114.B", "ECAM350.55.B"), "False positive match"
    print("[OK] No match: ECAM22.114.B != ECAM350.55.B")
    
    print("\n[SUCCESS] All matching tests passed")
    return True


def test_price_cleaning():
    """Test price string cleaning"""
    print("\n" + "="*60)
    print("TEST: Price Cleaning")
    print("="*60)
    
    from scrapers.alta.alta_bs4_scraper import AltaBS4Scraper
    scraper = AltaBS4Scraper()
    
    test_cases = [
        ("1499", 1499.0),
        ("549", 549.0),
        ("1,499", 1499.0),
        ("799 GEL", 799.0),
        ("  2649  ", 2649.0),
        ('"1859"', 1859.0),
    ]
    
    passed = 0
    for price_str, expected in test_cases:
        result = scraper.clean_price(price_str)
        if result == expected:
            print(f"[OK] '{price_str}' -> {result}")
            passed += 1
        else:
            print(f"[FAIL] '{price_str}' -> {result} (expected {expected})")
    
    print(f"\n[RESULT] {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print(" "*20 + "ALTA SCRAPER TEST SUITE")
    print("="*70)
    
    results = []
    
    # Unit tests (fast)
    print("\n### UNIT TESTS ###")
    results.append(("Model Extraction", test_model_extraction()))
    results.append(("Model Matching", test_model_matching()))
    results.append(("Price Cleaning", test_price_cleaning()))
    
    # Integration test (slower)
    print("\n### INTEGRATION TEST ###")
    results.append(("ALTA BS4 Quick Test", test_alta_bs4_scraper_quick()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

