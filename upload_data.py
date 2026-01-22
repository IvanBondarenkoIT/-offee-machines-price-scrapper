#!/usr/bin/env python3
"""
Simple file uploader for Coffee Price Monitor
Reads API credentials from environment variables

Usage:
1. Create .env file with:
   API_KEY=your_api_key_here
   API_UPLOAD_URL=https://your-app.up.railway.app/api/upload
2. Run: python upload_data.py
"""
import requests
import os
from pathlib import Path

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def upload_file():
    # Read from environment variables (set in .env file)
    api_url = os.environ.get('API_UPLOAD_URL', 'https://your-app.up.railway.app/api/upload')
    api_key = os.environ.get('API_KEY')
    
    if not api_key:
        print("[ERROR] API_KEY environment variable is required!")
        print("Create .env file with:")
        print("  API_KEY=your_api_key_here")
        print("  API_UPLOAD_URL=https://your-app.up.railway.app/api/upload")
        return False
    
    # Find latest price comparison file
    data_dir = Path("data/output")
    files = list(data_dir.glob("price_comparison_*.xlsx"))
    
    if not files:
        print("[ERROR] No price comparison files found!")
        print(f"  Looking in: {data_dir.absolute()}")
        return False
    
    latest_file = max(files, key=lambda x: x.stat().st_mtime)
    print(f"[INFO] Uploading: {latest_file.name}")
    print(f"[INFO] File size: {latest_file.stat().st_size / 1024:.2f} KB")
    
    headers = {"X-API-Key": api_key}
    
    try:
        print(f"[INFO] Sending to: {api_url}")
        with open(latest_file, 'rb') as f:
            files_data = {"file": (latest_file.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            response = requests.post(api_url, headers=headers, files=files_data, timeout=60)
        
        if response.status_code == 200:
            print("[OK] Upload successful!")
            result = response.json()
            print(f"[INFO] Upload ID: {result.get('upload_id', 'N/A')}")
            print(f"[INFO] Upload Date: {result.get('upload_date', 'N/A')}")
            if 'statistics' in result:
                stats = result['statistics']
                print(f"[INFO] Products: {stats.get('total_products', 'N/A')}")
            return True
        else:
            print(f"[FAIL] Upload failed: {response.status_code}")
            print(f"[ERROR] Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timeout (60s)")
        return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection error - check API_UPLOAD_URL")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*80)
    print("COFFEE PRICE MONITOR - DATA UPLOADER")
    print("="*80)
    print()
    
    success = upload_file()
    
    if success:
        print("\n" + "="*80)
        print("[SUCCESS] Data uploaded to web application!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("[FAILED] Upload failed. Check errors above.")
        print("="*80)
    
    exit(0 if success else 1)
