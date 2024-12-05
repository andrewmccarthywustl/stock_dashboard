# server/api/__init__.py
# This is the initalization for the api
"""
API Package for Stock Portfolio Dashboard
"""
from flask import Blueprint
import os

# Package version
__version__ = '1.0.0'

# Create Blueprint for API
api = Blueprint('api', __name__)

# Import and register routes
from .routes.portfolio_bp import portfolio_bp

# Export all components
__all__ = [
    'api',
    'portfolio_bp'
]

# Package configuration - define the correct paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(API_DIR, 'config')
DATA_DIR = os.path.join(API_DIR, 'data')
LOG_DIR = os.path.join(API_DIR, 'logs')

# Ensure directories exist
for directory in [CONFIG_DIR, DATA_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

def init_app(app):
    """Initialize API with Flask app"""
    # Register blueprints
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    
    # Initialize core components
    from .core import initialize_core
    initialize_core(app)
    
    # Initialize services
    from .services import init_services
    init_services(app)
    
    # Initialize repositories
    from .repositories import init_repositories
    init_repositories(app)
    
    return app