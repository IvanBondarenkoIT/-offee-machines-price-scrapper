"""
Test script for Flask web application
Tests basic functionality locally before deployment
"""
import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("\n=== Testing Imports ===")
    
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
        
        print("\n[OK] All imports successful!")
        return True
    except Exception as e:
        print(f"\n[FAIL] Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """Test Flask app creation"""
    print("\n=== Testing App Creation ===")
    
    try:
        from web_app.app import create_app
        
        # Set test database URL
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
        os.environ['API_KEY'] = 'test-api-key'
        
        app = create_app('development')
        print("✓ App created")
        
        print(f"  - Name: {app.name}")
        print(f"  - Debug: {app.debug}")
        print(f"  - Testing: {app.testing}")
        
        # Check blueprints
        blueprints = list(app.blueprints.keys())
        print(f"  - Blueprints: {', '.join(blueprints)}")
        
        expected_blueprints = ['main', 'auth', 'comparison', 'history', 'api']
        for bp in expected_blueprints:
            if bp in blueprints:
                print(f"    ✓ {bp}")
            else:
                print(f"    ✗ {bp} missing")
                return False
        
        print("\n✓ App creation successful!")
        return True
    except Exception as e:
        print(f"\n✗ App creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_routes():
    """Test that all routes are registered"""
    print("\n=== Testing Routes ===")
    
    try:
        from web_app.app import create_app
        
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        os.environ['SECRET_KEY'] = 'test-secret-key'
        
        app = create_app('development')
        
        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append((rule.endpoint, rule.rule))
        
        # Expected routes
        expected_routes = [
            'main.index',
            'main.dashboard',
            'auth.login',
            'auth.logout',
            'comparison.index',
            'history.index',
            'api.upload',
            'api.health'
        ]
        
        print("Checking expected routes:")
        for endpoint in expected_routes:
            found = any(r[0] == endpoint for r in routes)
            if found:
                route_rule = next(r[1] for r in routes if r[0] == endpoint)
                print(f"  ✓ {endpoint:30} → {route_rule}")
            else:
                print(f"  ✗ {endpoint:30} → NOT FOUND")
                return False
        
        print(f"\nTotal routes: {len(routes)}")
        print("\n✓ All routes registered!")
        return True
    except Exception as e:
        print(f"\n✗ Routes test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_database_models():
    """Test database models"""
    print("\n=== Testing Database Models ===")
    
    try:
        from web_app.app import create_app
        from web_app.database import db
        from web_app.models import User, Upload, Product, CompetitorPrice, Statistic
        
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        os.environ['SECRET_KEY'] = 'test-secret-key'
        
        app = create_app('development')
        
        with app.app_context():
            # Create tables
            db.create_all()
            print("✓ Tables created")
            
            # Test User model
            user = User(username='test', email='test@test.com', role='admin')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            print("✓ User model works")
            
            # Verify password
            assert user.check_password('password123')
            assert not user.check_password('wrong')
            print("✓ Password hashing works")
            
            # Test Flask-Login properties
            assert user.is_authenticated
            assert user.is_active
            assert not user.is_anonymous
            print("✓ Flask-Login integration works")
            
            # Clean up
            db.drop_all()
            
        # Remove test database
        test_db = Path('test.db')
        if test_db.exists():
            test_db.unlink()
        
        print("\n✓ Database models work!")
        return True
    except Exception as e:
        print(f"\n✗ Database test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """Test API health endpoint"""
    print("\n=== Testing API Endpoint ===")
    
    try:
        from web_app.app import create_app
        
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        os.environ['SECRET_KEY'] = 'test-secret-key'
        
        app = create_app('development')
        client = app.test_client()
        
        # Test health endpoint
        response = client.get('/api/health')
        assert response.status_code == 200
        print("✓ Health endpoint responds")
        
        data = response.get_json()
        assert data['status'] == 'ok'
        print("✓ Health endpoint returns correct data")
        
        print("\n✓ API endpoint works!")
        return True
    except Exception as e:
        print(f"\n✗ API test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_templates_exist():
    """Test that all template files exist"""
    print("\n=== Testing Templates ===")
    
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
            print(f"  ✓ {template}")
        else:
            print(f"  ✗ {template} NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("\n✓ All templates exist!")
        return True
    else:
        print("\n✗ Some templates missing!")
        return False

def test_static_files_exist():
    """Test that static files exist"""
    print("\n=== Testing Static Files ===")
    
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
            print(f"  ✓ {file} ({size} bytes)")
        else:
            print(f"  ✗ {file} NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("\n✓ All static files exist!")
        return True
    else:
        print("\n✗ Some static files missing!")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print(" Flask Web Application - Test Suite")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("App Creation", test_app_creation),
        ("Routes", test_routes),
        ("Database Models", test_database_models),
        ("API Endpoint", test_api_endpoint),
        ("Templates", test_templates_exist),
        ("Static Files", test_static_files_exist)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print(" Test Summary")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:10} {name}")
    
    print("\n" + "="*60)
    print(f" Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\n✓ All tests passed! Ready for deployment.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please fix before deployment.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

