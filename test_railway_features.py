"""
Test script for Railway features
Tests all API endpoints and functionality
"""

import requests
import time
from pathlib import Path
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"  # Change to Railway URL for production testing

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def test_health():
    """Test health endpoint"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Health check PASSED")
            return True
        else:
            print("❌ Health check FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_inventory_info():
    """Test inventory info endpoint"""
    print_section("TEST 2: Inventory Info")
    
    try:
        response = requests.get(f"{BASE_URL}/inventory/info")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Has file: {data.get('has_file')}")
        print(f"Message: {data.get('message')}")
        
        if data.get('has_file'):
            print(f"📅 Дата актуальности: {data.get('uploaded_at_formatted')}")
            print(f"📦 Товаров: {data.get('products_count')}")
        
        print("✅ Inventory info PASSED")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_upload_inventory(file_path=None):
    """Test inventory upload"""
    print_section("TEST 3: Upload Inventory File")
    
    if file_path is None:
        # Try to find inventory file
        possible_paths = [
            "data/inbox/остатки.xls",
            "data/inbox/остатки.xlsx",
            "остатки.xls",
            "остатки.xlsx"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                file_path = path
                break
        
        if file_path is None:
            print("⚠️ No inventory file found, skipping upload test")
            return True
    
    try:
        print(f"Uploading: {file_path}")
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/inventory/upload", files=files)
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Message: {data.get('message')}")
        print(f"📅 Дата: {data.get('uploaded_at_formatted')}")
        print(f"📄 Файл: {data.get('filename')}")
        
        if response.status_code == 200:
            print("✅ Upload PASSED")
            return True
        else:
            print("❌ Upload FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_scrape_all():
    """Test scrape all endpoint"""
    print_section("TEST 4: Scrape All (background task)")
    
    try:
        response = requests.post(f"{BASE_URL}/scrape/all")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Message: {data.get('message')}")
        print(f"Started at: {data.get('started_at')}")
        
        if response.status_code == 200:
            print("✅ Scrape started PASSED")
            print("\n⏳ Checking status for 30 seconds...")
            
            # Check status for 30 seconds
            for i in range(6):
                time.sleep(5)
                status_response = requests.get(f"{BASE_URL}/status")
                status_data = status_response.json()
                print(f"  [{i+1}/6] Status: {status_data.get('current_status')} - {status_data.get('current_step', 'Running...')}")
                
                if status_data.get('current_status') == 'completed':
                    print("✅ Scraping COMPLETED!")
                    break
                elif status_data.get('current_status') == 'failed':
                    print(f"❌ Scraping FAILED: {status_data.get('error')}")
                    break
            
            return True
        else:
            print("❌ Scrape start FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_reports_list():
    """Test reports list endpoint"""
    print_section("TEST 5: Reports List")
    
    try:
        response = requests.get(f"{BASE_URL}/reports/list")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Reports found: {len(data)}")
        
        if len(data) > 0:
            print("\nRecent reports:")
            for report in data[:5]:
                print(f"  - {report['filename']} ({report['created_at']})")
        
        print("✅ Reports list PASSED")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_swagger_docs():
    """Test Swagger documentation"""
    print_section("TEST 6: Swagger Documentation")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Swagger docs PASSED")
            print(f"📖 Open in browser: {BASE_URL}/docs")
            return True
        else:
            print("❌ Swagger docs FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print(" RAILWAY FEATURES TEST SUITE".center(70))
    print("=" * 70)
    print(f"Testing: {BASE_URL}")
    print()
    
    results = {
        "Health Check": test_health(),
        "Inventory Info": test_inventory_info(),
        "Upload Inventory": test_upload_inventory(),
        "Scrape All": test_scrape_all(),
        "Reports List": test_reports_list(),
        "Swagger Docs": test_swagger_docs(),
    }
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30s} {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Application is ready for Railway!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check logs for details.")
    
    print("\n📝 Check logs at: logs/api_server.log")
    print(f"🌐 Open in browser: {BASE_URL}/")

if __name__ == "__main__":
    main()

