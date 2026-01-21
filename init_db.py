"""
Database initialization script
Creates tables and first admin user
"""
import os
from web_app.app import create_app
from web_app.database import db
from web_app.models import User

def init_database():
    """Initialize database with tables and admin user"""
    # Get config from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    with app.app_context():
        print("Initializing database...")
        
        # Create all tables
        db.create_all()
        print("✓ Tables created")
        
        # Create admin user if doesn't exist
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin = User.query.filter_by(username=admin_username).first()
        
        if not admin:
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@company.com')
            
            admin = User(
                username=admin_username,
                email=admin_email,
                role='admin'
            )
            admin.set_password(admin_password)
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"✓ Admin user created:")
            print(f"  Username: {admin_username}")
            print(f"  Email: {admin_email}")
            print(f"  Role: admin")
            print(f"\n⚠ Please change the default password after first login!")
        else:
            print(f"✓ Admin user already exists: {admin_username}")
        
        print("\n✓ Database initialization completed successfully!")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n✗ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

