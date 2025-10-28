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
        
        # Create tables if they don't exist (for development)
        db.create_all()

