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
            app.logger.info("Database tables ensured to exist.")
        except Exception as e:
            # Tables might already exist, that's OK
            app.logger.warning(f"Database tables might already exist or error creating: {e}")
            pass
        
        # Admin user creation disabled - using ENV-based authentication (SimpleUser)
        # Authentication now uses ADMIN_USERNAME and ADMIN_PASSWORD from environment variables
        # See web_app/utils/simple_user.py for implementation

