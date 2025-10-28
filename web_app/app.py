"""
Flask application factory
"""
from flask import Flask
from flask_login import LoginManager
from web_app.config import config
from web_app.database import db, init_db

# Initialize Flask-Login
login_manager = LoginManager()

def create_app(config_name='default'):
    """
    Create and configure Flask application
    
    Args:
        config_name: Configuration name ('development', 'production', 'default')
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_db(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from web_app.models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from web_app.routes.main import bp as main_bp
    from web_app.routes.auth import bp as auth_bp
    from web_app.routes.comparison import bp as comparison_bp
    from web_app.routes.history import bp as history_bp
    from web_app.routes.api import bp as api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(comparison_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(api_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

