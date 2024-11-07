# server/api/config/config.py
import os
from datetime import timedelta
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    
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
    
    # Stock Data Provider Settings
    STOCK_DATA_PROVIDER = os.getenv('STOCK_DATA_PROVIDER', 'alpha_vantage')
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    ALPHA_VANTAGE_BATCH_SIZE = 100
    FMP_API_KEY = os.getenv('FMP_API_KEY')  # Keep for backwards compatibility
    
    # Redis settings
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_URL = os.getenv('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}')
    
    # Cache settings
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX = 'stock_portfolio:'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_REDIS_URL = REDIS_URL
    
    # Stock data cache timeouts (in seconds)
    CACHE_TIMEOUTS = {
        'stock_info': 3600,        # 1 hour
        'batch_quotes': 60,        # 1 minute
        'market_status': 60,       # 1 minute
        'search_results': 3600,    # 1 hour
        'portfolio': 300,          # 5 minutes
        'transactions': 300        # 5 minutes
    }
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STRATEGY = 'redis'
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100/minute"
    RATELIMIT_HEADERS_ENABLED = True
    
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
    
    # Circuit Breaker
    CIRCUIT_BREAKER_ENABLED = True
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
    CIRCUIT_BREAKER_RESET_TIMEOUT = 60  # seconds
    
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
        
        # Initialize provider-specific settings
        cls.init_provider_settings(app)
        
        return app

    @classmethod
    def init_provider_settings(cls, app) -> None:
        """Initialize stock data provider specific settings"""
        provider = cls.STOCK_DATA_PROVIDER.lower()
        
        if provider == 'alpha_vantage':
            if not cls.ALPHA_VANTAGE_API_KEY:
                raise ValueError("ALPHA_VANTAGE_API_KEY must be set")
                
            app.config['STOCK_PROVIDER_SETTINGS'] = {
                'api_key': cls.ALPHA_VANTAGE_API_KEY,
                'batch_size': cls.ALPHA_VANTAGE_BATCH_SIZE,
                'rate_limit': {
                    'calls': 150,
                    'per_seconds': 60
                }
            }
        elif provider == 'fmp':  # For backwards compatibility
            if not cls.FMP_API_KEY:
                raise ValueError("FMP_API_KEY must be set")
                
            app.config['STOCK_PROVIDER_SETTINGS'] = {
                'api_key': cls.FMP_API_KEY,
                'rate_limit': {
                    'calls': 300,
                    'per_seconds': 60
                }
            }
        else:
            raise ValueError(f"Unsupported stock data provider: {provider}")

class DevelopmentConfig(Config):
    """Development configuration"""
    ENV = 'development'
    DEBUG = True
    
    # Development-specific settings
    SQLALCHEMY_ECHO = True
    TEMPLATES_AUTO_RELOAD = True
    
    # Shorter cache timeouts for development
    CACHE_TIMEOUTS = {
        'stock_info': 300,         # 5 minutes
        'batch_quotes': 30,        # 30 seconds
        'market_status': 30,       # 30 seconds
        'search_results': 300,     # 5 minutes
        'portfolio': 60,           # 1 minute
        'transactions': 60         # 1 minute
    }

class TestingConfig(Config):
    """Testing configuration"""
    ENV = 'testing'
    TESTING = True
    DEBUG = True
    
    # Testing-specific settings
    PORTFOLIO_FILE = os.path.join(Config.DATA_DIR, 'test_portfolio.json')
    TRANSACTION_FILE = os.path.join(Config.DATA_DIR, 'test_transactions.json')
    
    # Use memory storage for testing
    CACHE_TYPE = 'simple'
    SESSION_TYPE = 'filesystem'
    
    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False

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
    
    # Longer cache timeouts for production
    CACHE_TIMEOUTS = {
        'stock_info': 7200,        # 2 hours
        'batch_quotes': 60,        # 1 minute
        'market_status': 60,       # 1 minute
        'search_results': 7200,    # 2 hours
        'portfolio': 300,          # 5 minutes
        'transactions': 300        # 5 minutes
    }

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