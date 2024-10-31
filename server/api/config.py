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
    
    # External APIs
    FMP_API_KEY = os.getenv('FMP_API_KEY')
    FMP_API_BASE_URL = 'https://financialmodelingprep.com/api/v3'
    
    # Redis settings
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_URL = os.getenv('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}')
    
    # Cache settings
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_KEY_PREFIX = 'stock_portfolio:'
    CACHE_REDIS_URL = REDIS_URL
    
    # Session settings
    SESSION_TYPE = 'redis'
    SESSION_REDIS = REDIS_URL
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-Request-ID']
    
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
    BATCH_QUOTE_SIZE = 100  # maximum number of symbols per batch request
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
        
        # Additional initialization can be added here
        return app

class DevelopmentConfig(Config):
    """Development configuration"""
    ENV = 'development'
    DEBUG = True
    
    # Development-specific settings
    SQLALCHEMY_ECHO = True
    TEMPLATES_AUTO_RELOAD = True

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