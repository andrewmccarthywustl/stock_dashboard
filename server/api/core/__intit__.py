# server/api/core/__init__.py
from .middleware import (
    setup_middleware,
    request_validator,
    require_json,
    validate_schema,
    ErrorHandler
)
from .rate_limiter import RateLimiter
from .circuit_breaker import CircuitBreaker
from .exceptions import (
    APIError,
    ValidationError,
    RateLimitError,
    CircuitBreakerError,
    CacheError
)
from redis import Redis
from flask import Flask
import logging

logger = logging.getLogger(__name__)

# Create singleton instances
error_handler = ErrorHandler()
rate_limiter = None
circuit_breaker = None

def initialize_core(app: Flask) -> None:
    """Initialize all core components with app context"""
    global rate_limiter, circuit_breaker
    
    try:
        # Initialize Redis if configured
        if app.config.get('RATELIMIT_ENABLED'):
            redis_client = Redis(
                host=app.config.get('REDIS_HOST', 'localhost'),
                port=app.config.get('REDIS_PORT', 6379),
                password=app.config.get('REDIS_PASSWORD'),
                db=app.config.get('REDIS_DB', 0),
                decode_responses=True
            )
            
            # Initialize rate limiter
            rate_limiter = RateLimiter(
                redis_client=redis_client,
                limit=app.config.get('RATELIMIT_DEFAULT', 100),
                window=app.config.get('RATELIMIT_WINDOW', 60),
                by_ip=app.config.get('RATELIMIT_BY_IP', True)
            )
            
        # Initialize circuit breaker
        if app.config.get('CIRCUIT_BREAKER_ENABLED'):
            circuit_breaker = CircuitBreaker(
                failure_threshold=app.config.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5),
                reset_timeout=app.config.get('CIRCUIT_BREAKER_RESET_TIMEOUT', 60),
                half_open_timeout=app.config.get('CIRCUIT_BREAKER_HALF_OPEN_TIMEOUT', 30)
            )
            
        # Initialize error handler
        error_handler.init_app(app)
        
        logger.info("Core components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize core components: {str(e)}")
        raise

__all__ = [
    'setup_middleware',
    'initialize_core',
    'request_validator',
    'require_json',
    'validate_schema',
    'error_handler',
    'rate_limiter',
    'circuit_breaker',
    'APIError',
    'ValidationError',
    'RateLimitError',
    'CircuitBreakerError',
    'CacheError'
]