"""
Simple user class for ENV-based authentication (no database required)
"""
from flask_login import UserMixin
import os


class SimpleUser(UserMixin):
    """
    Simple user class that uses environment variables for authentication
    No database required - all authentication is done via ENV variables
    """
    
    def __init__(self):
        """Initialize simple user from environment variables"""
        self.id = 1  # Fixed ID for single admin user
        self.username = os.environ.get('ADMIN_USERNAME', 'admin')
        self.email = os.environ.get('ADMIN_EMAIL', 'admin@company.com')
        self.role = 'admin'  # Always admin role
        # Note: is_active and is_authenticated are properties from UserMixin (default True)
    
    def __repr__(self):
        return f'<SimpleUser {self.username}>'
    
    def get_id(self):
        """Return user ID (required by Flask-Login)"""
        return str(self.id)
    
    @staticmethod
    def verify_login(username, password):
        """
        Verify login credentials against environment variables
        
        Args:
            username: Username to verify
            password: Password to verify
        
        Returns:
            bool: True if credentials match ENV variables, False otherwise
        """
        env_username = os.environ.get('ADMIN_USERNAME', '').strip()
        env_password = os.environ.get('ADMIN_PASSWORD', '').strip()
        
        # Fail if credentials are not set in ENV
        if not env_username or not env_password:
            return False
        
        # Compare credentials (case-sensitive)
        username_match = username.strip() == env_username
        password_match = password == env_password
        
        return username_match and password_match
    
    @staticmethod
    def get_instance():
        """
        Get SimpleUser instance (singleton pattern)
        
        Returns:
            SimpleUser: User instance
        """
        return SimpleUser()

