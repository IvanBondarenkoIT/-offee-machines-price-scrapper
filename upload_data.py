#!/usr/bin/env python3
"""
Upload price comparison file to web frontend
Reads configuration from .env file for security
"""
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def upload_file():
    """Upload latest price comparison file to web API"""
    
    # Get configuration from .env
    api_url = os.getenv('API_UPLOAD_URL')
    api_key = os.getenv('API_KEY')
    
    # Validate configuration
    if not api_url:
        print("[ERROR] API_UPLOAD_URL not set in .env file")
        print("        Add: API_UPLOAD_URL=https://your-server.com/api/upload")
        return False
    
    if not api_key:
        print("[ERROR] API_KEY not set in .env file")
        print("        Add: API_KEY=your_api_key_here")
        return False
    
    # Find latest price comparison file
    data_dir = Path("data/output")
    files = list(data_dir.glob("price_comparison_*.xlsx"))
    
    if not files:
        print("[ERROR] No price comparison files found in data/output/")
        return False
    
    latest_file = max(files, key=os.path.getctime)
    print(f"[INFO] Found file: {latest_file.name}")
    print(f"[INFO] Uploading to: {api_url}")
    
    headers = {"X-API-Key": api_key}
    
    try:
        with open(latest_file, 'rb') as f:
            files_data = {
                "file": (
                    latest_file.name, 
                    f, 
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            }
            
            print("[INFO] Sending request...")
            response = requests.post(
                api_url, 
                headers=headers, 
                files=files_data,
                timeout=60  # 60 seconds timeout
            )
        
        if response.status_code == 200:
            print("[OK] Upload successful!")
            try:
                result = response.json()
                print(f"     Response: {result}")
            except:
                print(f"     Response: {response.text[:200]}")
            return True
        else:
            print(f"[FAIL] Upload failed: HTTP {response.status_code}")
            print(f"       Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timeout (>60 seconds)")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection error: {e}")
        print("        Check that API_UPLOAD_URL is correct and server is accessible")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("="*80)
    print("UPLOADING PRICE COMPARISON TO WEB FRONTEND")
    print("="*80)
    
    success = upload_file()
    
    if success:
        print("\n" + "="*80)
        print("UPLOAD COMPLETE")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("UPLOAD FAILED")
        print("="*80)
        print("\nTroubleshooting:")
        print("1. Check .env file exists in project root")
        print("2. Verify API_UPLOAD_URL is set correctly")
        print("3. Verify API_KEY is set correctly")
        print("4. Check internet connection")
        print("5. Verify web frontend is running")
    
    exit(0 if success else 1)

