# server/api/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Environment
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = ENV == 'development'
    TESTING = ENV == 'testing'
    
    # Application
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8080))
    USE_RELOADER = DEBUG
    
    # API Settings
    API_PREFIX = '/api'
    API_VERSION = '1.0'
    API_TITLE = 'Stock Portfolio API'
    API_DESCRIPTION = 'API for managing stock portfolio and trades'
    
    # Directory paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    
    # File paths
    PORTFOLIO_FILE = os.path.join(DATA_DIR, 'portfolio.json')
    TRANSACTION_FILE = os.path.join(DATA_DIR, 'transactions.json')
    
    # Alpha Vantage Settings
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    ALPHA_VANTAGE_RATE_LIMIT = 150  # requests per minute
    ALPHA_VANTAGE_BATCH_SIZE = 100  # maximum symbols per request
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-Request-ID']
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Performance
    SLOW_REQUEST_THRESHOLD = float(os.getenv('SLOW_REQUEST_THRESHOLD', 0.5))  # seconds
    MAX_THREAD_POOL_SIZE = int(os.getenv('MAX_THREAD_POOL_SIZE', 20))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))  # seconds
    
    # Stock Service
    STOCK_DATA_CACHE_TIME = 60  # seconds
    MARKET_HOURS_START = "09:30"  # Eastern Time
    MARKET_HOURS_END = "16:00"    # Eastern Time
    
    # Portfolio Settings
    MAX_POSITIONS = 1000
    MAX_TRANSACTIONS = 10000
    MIN_TRADE_AMOUNT = 1
    MAX_TRADE_AMOUNT = 1000000
    
    @classmethod
    def init_app(cls, app):
        """Initialize application configuration"""
        # Ensure required directories exist
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        
        # Set Flask config
        app.config.from_object(cls)
        
        # Validate required settings
        if not cls.ALPHA_VANTAGE_API_KEY:
            raise ValueError("ALPHA_VANTAGE_API_KEY must be set in environment variables")
        
        return app

class DevelopmentConfig(Config):
    """Development configuration"""
    ENV = 'development'
    DEBUG = True
    
    # Development-specific settings
    TEMPLATES_AUTO_RELOAD = True

class TestingConfig(Config):
    """Testing configuration"""
    ENV = 'testing'
    TESTING = True
    DEBUG = True
    
    # Testing-specific settings
    PORTFOLIO_FILE = os.path.join(Config.DATA_DIR, 'test_portfolio.json')
    TRANSACTION_FILE = os.path.join(Config.DATA_DIR, 'test_transactions.json')

class ProductionConfig(Config):
    """Production configuration"""
    ENV = 'production'
    DEBUG = False
    
    # Production-specific settings
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Stricter CORS in production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    
    # Production logging
    LOG_LEVEL = 'WARNING'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])