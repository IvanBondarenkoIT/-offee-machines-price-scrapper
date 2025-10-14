"""
Test scraping with pure BeautifulSoup (NO Selenium)
For Railway compatibility testing
"""

import requests
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_scrape_endpoint():
    """Test scraping through API"""
    print("=" * 70)
    print(" TESTING SCRAPING VIA API")
    print("=" * 70)
    print(f"API URL: {BASE_URL}")
    print()
    
    # Start scraping
    print("1. Starting scraping...")
    try:
        response = requests.post(f"{BASE_URL}/scrape/all")
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Message: {data.get('message')}")
        print(f"   Started at: {data.get('started_at')}")
        print()
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to start: {data}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False
    
    # Check status
    print("2. Checking status every 5 seconds...")
    for i in range(12):  # Check for 1 minute
        time.sleep(5)
        
        try:
            response = requests.get(f"{BASE_URL}/status")
            data = response.json()
            status = data.get('current_status')
            step = data.get('current_step', 'Running...')
            
            print(f"   [{i+1}/12] Status: {status} - {step}")
            
            if status == 'completed':
                print()
                print("[SUCCESS] Scraping completed!")
                print(f"   Products scraped: {data.get('products_scraped')}")
                return True
                
            elif status == 'failed':
                print()
                print(f"[ERROR] Scraping failed!")
                print(f"   Error: {data.get('error')}")
                return False
                
        except Exception as e:
            print(f"   [ERROR] Status check failed: {e}")
    
    print()
    print("[TIMEOUT] Still running after 1 minute")
    print("   Check /status endpoint manually")
    return None

def check_output_files():
    """Check if output files were created"""
    print()
    print("=" * 70)
    print(" CHECKING OUTPUT FILES")
    print("=" * 70)
    
    output_dir = Path("data/output")
    files = list(output_dir.glob("*.xlsx")) + list(output_dir.glob("*.csv"))
    
    if files:
        print(f"Found {len(files)} files:")
        for f in files:
            print(f"   - {f.name} ({f.stat().st_size} bytes)")
        return True
    else:
        print("   No files found in data/output/")
        return False

if __name__ == "__main__":
    print()
    result = test_scrape_endpoint()
    
    if result:
        check_output_files()
    
    print()
    print("=" * 70)
    print(" TEST COMPLETE")
    print("=" * 70)
    
    if result:
        print("[SUCCESS] Scraping works!")
    else:
        print("[INFO] Check logs for details")
        print("   Logs: logs/api_server.log")

