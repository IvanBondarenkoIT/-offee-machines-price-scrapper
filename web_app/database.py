"""
Database connection and initialization
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Import all models to ensure they are registered with SQLAlchemy
        from web_app.models import user, upload, product, competitor_price, statistic
        
        # Create tables if they don't exist (safe for production)
        try:
            db.create_all()
        except Exception as e:
            # Tables might already exist, that's OK
            print(f"Database tables already exist or error creating: {e}")
            pass
        
        # Create admin user if not exists
        try:
            from web_app.models.user import User
            import os
            
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@company.com')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'ChangeThisPassword123!')
            
            admin_user = User.query.filter_by(username=admin_username).first()
            if not admin_user:
                admin_user = User(
                    username=admin_username,
                    email=admin_email,
                    role='admin'
                )
                admin_user.set_password(admin_password)
                db.session.add(admin_user)
                db.session.commit()
                print(f"Admin user '{admin_username}' created successfully")
            else:
                # Update password if changed
                admin_user.set_password(admin_password)
                admin_user.email = admin_email
                db.session.commit()
                print(f"Admin user '{admin_username}' updated")
                
        except Exception as e:
            print(f"Error creating admin user: {e}")
            pass

