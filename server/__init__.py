# server/__init__.py
#This is the intialization for the server
"""
Stock Portfolio Dashboard Server
"""

import os
from flask import Flask
from .api import init_app as init_api

# Version information
__version__ = '1.0.0'
__author__ = 'Your Name'
__description__ = 'Stock Portfolio Dashboard API Server'

# Only define base directories here
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Remove these lines as they should be managed by api package
# DATA_DIR = os.path.join(BASE_DIR, 'server', 'data')
# LOG_DIR = os.path.join(BASE_DIR, 'server', 'logs')

# Remove directory creation from here
# os.makedirs(DATA_DIR, exist_ok=True)
# os.makedirs(LOG_DIR, exist_ok=True)

def create_app(config_name=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Initialize API
    init_api(app)
    
    return app

__all__ = [
    'create_app',
    '__version__',
    '__author__',
    '__description__',
    'BASE_DIR'
]