"""
Test Runner - Quick health check for scrapers
Run this periodically to ensure nothing is broken
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tests.test_alta_scraper import run_all_tests


def main():
    """Main test runner"""
    print("""
======================================================================
                  SCRAPER HEALTH CHECK
                                                                 
  This will run quick tests to verify scrapers are working       
  Expected time: ~30-60 seconds                                  
======================================================================
""")
    
    print("\nStarting tests...\n")
    
    success = run_all_tests()
    
    if success:
        print("""
======================================================================
                    [SUCCESS] ALL TESTS PASSED
                                                                 
  Scrapers are working correctly!
======================================================================
""")
    else:
        print("""
======================================================================
                    [WARNING] SOME TESTS FAILED
                                                                 
  Please check the output above for details
======================================================================
""")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

