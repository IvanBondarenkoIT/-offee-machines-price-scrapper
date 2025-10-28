"""
Simple test script for Flask web application - imports only
No database required
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

def test_imports():
    """Test that all modules can be imported"""
    print("\n=== Testing Imports ===\n")
    
    try:
        from web_app.app import create_app
        print("[OK] Flask app import")
        
        from web_app.database import db, init_db
        print("[OK] Database import")
        
        from web_app.models import User, Upload, Product, CompetitorPrice, Statistic
        print("[OK] Models import")
        
        from web_app.routes import auth, main, comparison, history, api
        print("[OK] Routes import")
        
        from web_app.services import dashboard_service, comparison_service, history_service, upload_service
        print("[OK] Services import")
        
        from web_app.utils import decorators, formatters
        print("[OK] Utils import")
        
        print("\n[SUCCESS] All imports successful!")
        return True
    except Exception as e:
        print(f"\n[FAIL] Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_templates_exist():
    """Test that all template files exist"""
    print("\n=== Testing Templates ===\n")
    
    templates_dir = Path('web_app/templates')
    
    required_templates = [
        'base.html',
        'auth/login.html',
        'dashboard/index.html',
        'comparison/index.html',
        'history/index.html',
        'components/navbar.html',
        'components/sidebar.html',
        'components/alerts.html',
        'errors/404.html',
        'errors/500.html'
    ]
    
    all_exist = True
    for template in required_templates:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"  [OK] {template}")
        else:
            print(f"  [FAIL] {template} NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("\n[SUCCESS] All templates exist!")
        return True
    else:
        print("\n[FAIL] Some templates missing!")
        return False

def test_static_files_exist():
    """Test that static files exist"""
    print("\n=== Testing Static Files ===\n")
    
    static_dir = Path('web_app/static')
    
    required_files = [
        'css/main.css',
        'js/main.js'
    ]
    
    all_exist = True
    for file in required_files:
        file_path = static_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  [OK] {file} ({size} bytes)")
        else:
            print(f"  [FAIL] {file} NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("\n[SUCCESS] All static files exist!")
        return True
    else:
        print("\n[FAIL] Some static files missing!")
        return False

def test_deployment_files():
    """Test that deployment files exist"""
    print("\n=== Testing Deployment Files ===\n")
    
    required_files = [
        'Dockerfile',
        'railway.json',
        '.dockerignore',
        'init_db.py',
        'run_web.py',
        'requirements-web.txt',
        'RAILWAY_DEPLOYMENT.md'
    ]
    
    all_exist = True
    for file in required_files:
        file_path = Path(file)
        if file_path.exists():
            print(f"  [OK] {file}")
        else:
            print(f"  [FAIL] {file} NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("\n[SUCCESS] All deployment files exist!")
        return True
    else:
        print("\n[FAIL] Some deployment files missing!")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print(" Flask Web Application - Quick Test (No Database)")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Templates", test_templates_exist),
        ("Static Files", test_static_files_exist),
        ("Deployment Files", test_deployment_files)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n[FAIL] Test '{name}' crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print(" Test Summary")
    print("="*60 + "\n")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status:10} {name}")
    
    print("\n" + "="*60)
    print(f" Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Ready for deployment.")
        print("\nNOTE: Database tests skipped (no PostgreSQL running locally)")
        print("Database functionality will be tested on Railway after deployment.")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} test(s) failed. Please fix before deployment.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

