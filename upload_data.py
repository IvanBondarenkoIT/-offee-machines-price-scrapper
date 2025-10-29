#!/usr/bin/env python3
"""
Simple file uploader for Coffee Price Monitor
"""
import requests
import os
from pathlib import Path

def upload_file():
    api_url = "https://cooperative-stillness-production.up.railway.app/api/upload"
    api_key = "x4RVIwxMQq3Z9DC-o62GRYC0sfBB5IwnaoatMi7wUKw"
    
    # Find latest price comparison file
    data_dir = Path("data/output")
    files = list(data_dir.glob("price_comparison_*.xlsx"))
    
    if not files:
        print("No price comparison files found!")
        return False
    
    latest_file = max(files, key=os.path.getctime)
    print(f"Uploading: {latest_file}")
    
    headers = {"X-API-Key": api_key}
    
    try:
        with open(latest_file, 'rb') as f:
            files_data = {"file": (latest_file.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            response = requests.post(api_url, headers=headers, files=files_data)
        
        if response.status_code == 200:
            print("[OK] Upload successful!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"[FAIL] Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

if __name__ == "__main__":
    upload_file()
