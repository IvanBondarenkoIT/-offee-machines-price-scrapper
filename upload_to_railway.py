"""
Upload generated reports from local PC to Railway
Run this script after local scraping is complete
"""

import requests
import sys
from pathlib import Path
from typing import List
import json

# Railway API configuration
RAILWAY_URL = "https://offee-machines-price-scrapper-production.up.railway.app"
# For local testing: RAILWAY_URL = "http://localhost:8080"

def find_latest_reports(output_dir: Path = Path("data/output")) -> List[Path]:
    """Find all report files in output directory"""
    reports = []
    
    # Find all Excel, Word, and PDF files
    for pattern in ["*.xlsx", "*.docx", "*.pdf"]:
        reports.extend(output_dir.glob(pattern))
    
    # Sort by modification time, newest first
    reports.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    return reports

def upload_file_via_ftp(file_path: Path) -> bool:
    """
    Upload file to Railway using FTP/SFTP
    
    NOTE: Railway doesn't support direct file uploads via HTTP
    You need to use one of these methods:
    
    1. Mount Railway volume and use SFTP/rsync
    2. Use cloud storage (S3, GCS, etc.) and sync
    3. Use GitHub and pull from repo
    
    For now, we'll use METHOD 3: Git-based deployment
    """
    print(f"⚠️  Railway doesn't support direct file upload")
    print(f"📁 File ready to deploy: {file_path.name}")
    return True

def deploy_via_git(reports: List[Path]) -> bool:
    """
    Method: Commit reports to git and Railway will auto-deploy
    """
    import subprocess
    
    print("\n🔄 Deploying reports via Git...")
    
    try:
        # Check if there are changes
        result = subprocess.run(
            ["git", "status", "--porcelain", "data/output"],
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            print("✅ No new reports to deploy")
            return True
        
        # Add reports to git
        subprocess.run(["git", "add", "data/output/*.xlsx", "data/output/*.docx", "data/output/*.pdf"], check=True)
        
        # Commit
        commit_msg = f"Update reports - {len(reports)} files"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        # Push to trigger Railway deployment
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print(f"\n✅ Successfully deployed {len(reports)} reports to Railway!")
        print(f"🌐 View at: {RAILWAY_URL}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Git deployment failed: {e}")
        return False

def check_railway_status() -> bool:
    """Check if Railway service is online"""
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Railway is online: {RAILWAY_URL}")
            return True
        else:
            print(f"⚠️  Railway returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach Railway: {e}")
        return False

def main():
    """Main upload process"""
    print("=" * 60)
    print("📤 Upload Reports to Railway")
    print("=" * 60)
    
    # Find reports
    output_dir = Path("data/output")
    if not output_dir.exists():
        print(f"❌ Output directory not found: {output_dir}")
        sys.exit(1)
    
    reports = find_latest_reports(output_dir)
    
    if not reports:
        print("❌ No reports found in data/output/")
        print("💡 Run scraping first: python run_full_cycle.py")
        sys.exit(1)
    
    print(f"\n📊 Found {len(reports)} report(s):")
    for i, report in enumerate(reports[:10], 1):  # Show first 10
        size_kb = report.stat().st_size // 1024
        print(f"  {i}. {report.name} ({size_kb} KB)")
    
    # Check Railway status
    print("\n🔍 Checking Railway status...")
    check_railway_status()
    
    # Deploy via Git
    print("\n" + "=" * 60)
    choice = input("\n📤 Deploy reports to Railway via Git? (y/n): ").lower()
    
    if choice == 'y':
        success = deploy_via_git(reports)
        
        if success:
            print("\n" + "=" * 60)
            print("✅ DEPLOYMENT SUCCESSFUL!")
            print("=" * 60)
            print(f"\n🌐 Open in browser: {RAILWAY_URL}")
            print(f"📊 Total reports: {len(reports)}")
            print("\n💡 Railway will rebuild and deploy in ~2 minutes")
        else:
            print("\n❌ Deployment failed")
            sys.exit(1)
    else:
        print("\n⏸️  Deployment cancelled")
        print("\n💡 Alternative: Manually copy files to Railway volume")

if __name__ == "__main__":
    main()

