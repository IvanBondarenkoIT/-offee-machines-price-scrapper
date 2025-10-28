"""
Local data uploader script

This script uploads the latest price comparison Excel file
to the Railway web application via API.

Usage:
    python web_uploader/uploader.py
"""
import os
import sys
import glob
import configparser
import requests
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

class PriceDataUploader:
    """Upload price comparison data to web application"""
    
    def __init__(self, config_path='web_uploader/config.ini'):
        """Initialize uploader with configuration"""
        self.config = self.load_config(config_path)
        self.api_url = self.config.get('API', 'url')
        self.api_key = self.config.get('API', 'key')
        self.data_dir = Path(self.config.get('LOCAL', 'data_directory'))
    
    def load_config(self, config_path):
        """Load configuration from INI file"""
        config = configparser.ConfigParser()
        
        if not os.path.exists(config_path):
            print(f"[ERROR] Config file not found: {config_path}")
            print("[INFO] Creating default config file...")
            self.create_default_config(config_path)
            print(f"[INFO] Please edit {config_path} with your settings")
            sys.exit(1)
        
        config.read(config_path)
        return config
    
    def create_default_config(self, config_path):
        """Create default configuration file"""
        config = configparser.ConfigParser()
        
        config['API'] = {
            'url': 'https://your-app.railway.app/api/upload',
            'key': 'your-api-key-here'
        }
        
        config['LOCAL'] = {
            'data_directory': 'data/output/excel'
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            config.write(f)
    
    def find_latest_file(self):
        """
        Find the latest price comparison Excel file
        
        Returns:
            Path: Path to the latest file or None
        """
        pattern = str(self.data_dir / 'price_comparison_*.xlsx')
        files = glob.glob(pattern)
        
        if not files:
            print(f"[ERROR] No price comparison files found in: {self.data_dir}")
            print(f"[INFO] Looking for pattern: price_comparison_*.xlsx")
            return None
        
        # Sort by modification time, get the latest
        latest_file = max(files, key=os.path.getmtime)
        return Path(latest_file)
    
    def upload_file(self, file_path):
        """
        Upload file to web application
        
        Args:
            file_path: Path to Excel file
        
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"\n[INFO] Uploading file: {file_path.name}")
        print(f"[INFO] File size: {file_path.stat().st_size / 1024:.2f} KB")
        print(f"[INFO] Modified: {datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Prepare request
            headers = {
                'X-API-Key': self.api_key
            }
            
            with open(file_path, 'rb') as f:
                files = {
                    'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                }
                
                print(f"[INFO] Sending request to: {self.api_url}")
                print("[INFO] Please wait...")
                
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    files=files,
                    timeout=60
                )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    print("\n[SUCCESS] File uploaded successfully!")
                    print(f"[INFO] Upload ID: {data.get('upload_id')}")
                    print(f"[INFO] Upload Date: {data.get('upload_date')}")
                    
                    if 'statistics' in data:
                        stats = data['statistics']
                        print("\n=== Statistics ===")
                        print(f"Total Products: {stats.get('total_products', 0)}")
                        print(f"Total Value: {stats.get('total_value', 0):.2f} GEL")
                        print(f"Products Cheaper: {stats.get('products_cheaper', 0)}")
                        print(f"Products Expensive: {stats.get('products_expensive', 0)}")
                        print(f"No Competitors: {stats.get('products_no_competitors', 0)}")
                    
                    return True
                else:
                    print(f"\n[ERROR] Upload failed: {data.get('error', 'Unknown error')}")
                    return False
            
            elif response.status_code == 401:
                print("\n[ERROR] Authentication failed - Invalid API key")
                print("[INFO] Please check your API key in config.ini")
                return False
            
            elif response.status_code == 403:
                print("\n[ERROR] Access forbidden - Invalid API key")
                return False
            
            elif response.status_code == 400:
                try:
                    error = response.json().get('error', 'Bad request')
                    print(f"\n[ERROR] Bad request: {error}")
                except:
                    print(f"\n[ERROR] Bad request: {response.text}")
                return False
            
            else:
                print(f"\n[ERROR] Upload failed with status code: {response.status_code}")
                print(f"[ERROR] Response: {response.text}")
                return False
        
        except requests.exceptions.ConnectionError:
            print("\n[ERROR] Connection failed")
            print("[INFO] Please check:")
            print("  1. Your internet connection")
            print("  2. The API URL in config.ini")
            print("  3. That the web application is running")
            return False
        
        except requests.exceptions.Timeout:
            print("\n[ERROR] Request timeout (60 seconds)")
            print("[INFO] The file might be too large or the server is slow")
            return False
        
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """Run the uploader"""
        print("="*60)
        print(" Coffee Price Monitor - Data Uploader")
        print("="*60)
        
        # Find latest file
        print(f"\n[INFO] Looking for files in: {self.data_dir}")
        latest_file = self.find_latest_file()
        
        if not latest_file:
            return False
        
        print(f"[INFO] Found file: {latest_file.name}")
        
        # Confirm upload
        response = input("\n[PROMPT] Do you want to upload this file? (y/n): ").strip().lower()
        
        if response != 'y':
            print("[INFO] Upload cancelled")
            return False
        
        # Upload
        success = self.upload_file(latest_file)
        
        if success:
            print("\n[INFO] Data is now available on the web application")
            print(f"[INFO] Visit: {self.api_url.replace('/api/upload', '')}")
        
        return success

def main():
    """Main entry point"""
    uploader = PriceDataUploader()
    
    try:
        success = uploader.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

