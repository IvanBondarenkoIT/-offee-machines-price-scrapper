"""
Main entry point for Coffee Machines Price Scraper
"""
import sys
from scrapers.alta_selenium_scraper import main as run_alta_scraper


def main():
    """Main function"""
    print("=" * 70)
    print("Coffee Machines Price Scraper".center(70))
    print("DeLonghi Products from ALTA.ge".center(70))
    print("=" * 70)
    print()
    
    print("Starting ALTA scraper...")
    print()
    
    try:
        run_alta_scraper()
        print()
        print("[OK] Scraping completed successfully!")
        print("Check data/output/ folder for results")
        
    except KeyboardInterrupt:
        print("\n\n[WARNING] Scraping interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n[ERROR] Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

