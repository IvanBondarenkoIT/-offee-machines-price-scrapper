"""
Test script for Dim Kava scraper
Run this to test the scraper on individual brands or all brands
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from scrapers.dimkava.dimkava_bs4_scraper import DimKavaBS4Scraper
from config import DIMKAVA_CONFIG
import argparse


def test_single_brand(url: str):
    """Test scraper on a single brand URL"""
    scraper = DimKavaBS4Scraper()
    scraper.urls = [url]
    scraper.run()
    return scraper.products


def test_all_brands():
    """Test scraper on all brand URLs"""
    scraper = DimKavaBS4Scraper()
    scraper.run()
    return scraper.products


def main():
    parser = argparse.ArgumentParser(description="Test Dim Kava scraper")
    parser.add_argument(
        "--brand",
        choices=["delonghi", "melitta", "nivona", "all"],
        default="all",
        help="Brand to scrape (default: all)"
    )
    
    args = parser.parse_args()
    
    brand_urls = {
        "delonghi": "https://dimkava.ge/brand/delonghi/",
        "melitta": "https://dimkava.ge/brand/melita/",
        "nivona": "https://dimkava.ge/brand/nivona/",
    }
    
    expected_counts = {
        "delonghi": 42,
        "melitta": 22,
        "nivona": 10,
    }
    
    if args.brand == "all":
        print("Testing all brands...")
        products = test_all_brands()
        print(f"\n{'='*60}")
        print(f"TOTAL: {len(products)} products scraped")
        print(f"Expected: 74 (42+22+10)")
        print(f"{'='*60}")
    else:
        url = brand_urls[args.brand]
        expected = expected_counts[args.brand]
        print(f"Testing {args.brand} brand...")
        print(f"URL: {url}")
        print(f"Expected: {expected} products")
        print()
        products = test_single_brand(url)
        print(f"\n{'='*60}")
        print(f"RESULT: {len(products)} products scraped")
        print(f"Expected: {expected} products")
        if len(products) == expected:
            print("[OK] SUCCESS! All products collected.")
        elif len(products) > expected:
            print(f"[WARNING] Collected more than expected ({len(products)} > {expected})")
        else:
            print(f"[FAILED] Missing {expected - len(products)} products")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()

