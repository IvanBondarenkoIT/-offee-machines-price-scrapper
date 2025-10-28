"""
Run Flask web application
"""
import os
from web_app.app import create_app

# Get config from environment
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = config_name == 'development'
    
    print(f"Starting Flask application...")
    print(f"Environment: {config_name}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

