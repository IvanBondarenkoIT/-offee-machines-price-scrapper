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
        
        # Create admin user once (idempotent, safe for multi-worker startup)
        try:
            from web_app.models.user import User
            from sqlalchemy.exc import IntegrityError
            import os

            admin_username = os.environ.get('ADMIN_USERNAME')
            admin_email = os.environ.get('ADMIN_EMAIL')
            admin_password = os.environ.get('ADMIN_PASSWORD')

            if not admin_username or not admin_email or not admin_password:
                app.logger.warning("ADMIN_* env vars not fully set; skipping auto admin creation")
            else:
                existing = User.query.filter(
                    (User.username == admin_username) | (User.email == admin_email)
                ).first()
                if existing:
                    # Do not overwrite on every start
                    app.logger.info("Admin user already exists; skipping creation")
                else:
                    admin_user = User(
                        username=admin_username,
                        email=admin_email,
                        role='admin'
                    )
                    admin_user.set_password(admin_password)
                    db.session.add(admin_user)
                    try:
                        db.session.commit()
                        app.logger.info(f"Admin user '{admin_username}' created successfully")
                    except IntegrityError:
                        db.session.rollback()
                        app.logger.info("Admin creation raced with another worker; ignoring")
        except Exception as e:
            app.logger.warning(f"Error during admin auto-creation: {e}")

