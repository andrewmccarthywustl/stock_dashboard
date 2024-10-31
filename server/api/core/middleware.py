# server/api/core/middleware.py
from functools import wraps
from flask import request, g, current_app, Response
from typing import Callable, Any, Optional
import time
import uuid
import logging
from .exceptions import ValidationError, AuthenticationError
from .rate_limiter import RateLimiter
from .circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

# Global middleware instances
rate_limiter = None
circuit_breaker = None

def init_middleware(app):
    """Initialize middleware with application context"""
    global rate_limiter, circuit_breaker
    
    # Initialize rate limiter if Redis is configured
    if app.config.get('RATELIMIT_ENABLED'):
        from redis import Redis
        redis_client = Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            password=app.config['REDIS_PASSWORD'],
            db=app.config['REDIS_DB']
        )
        rate_limiter = RateLimiter(
            redis_client,
            limit=app.config.get('RATELIMIT_DEFAULT', 100),
            window=60
        )

    # Initialize circuit breaker
    if app.config.get('CIRCUIT_BREAKER_ENABLED'):
        circuit_breaker = CircuitBreaker(
            failure_threshold=app.config.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5),
            reset_timeout=app.config.get('CIRCUIT_BREAKER_RESET_TIMEOUT', 60)
        )

def request_validator(f: Callable) -> Callable:
    """Validate incoming requests"""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        # Validate content type for POST/PUT requests
        if request.method in ['POST', 'PUT']:
            if not request.is_json:
                raise ValidationError("Content-Type must be application/json")

        # Add request timestamp
        g.request_start_time = time.time()

        # Add request ID if not present
        if 'X-Request-ID' not in request.headers:
            g.request_id = str(uuid.uuid4())
        else:
            g.request_id = request.headers['X-Request-ID']

        return f(*args, **kwargs)
    return decorated_function

def add_cors_headers(response: Response) -> Response:
    """Add CORS headers to response"""
    response.headers['Access-Control-Allow-Origin'] = current_app.config.get('CORS_ORIGINS', '*')
    response.headers['Access-Control-Allow-Methods'] = ','.join(current_app.config.get('CORS_METHODS', ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']))
    response.headers['Access-Control-Allow-Headers'] = ','.join(current_app.config.get('CORS_ALLOW_HEADERS', ['Content-Type', 'Authorization', 'X-Request-ID']))
    return response

class ErrorHandler:
    """Error handler for the application"""
    
    def __init__(self):
        self.app = None

    def init_app(self, app):
        """Initialize error handler with app context"""
        self.app = app
        self.register_handlers()

    def register_handlers(self):
        """Register error handlers"""
        
        @self.app.errorhandler(ValidationError)
        def handle_validation_error(error):
            return self._create_error_response(error, 400)

        @self.app.errorhandler(AuthenticationError)
        def handle_auth_error(error):
            return self._create_error_response(error, 401)

        @self.app.errorhandler(Exception)
        def handle_generic_error(error):
            logger.exception("Unhandled exception")
            return self._create_error_response(
                "Internal Server Error",
                500
            )

    def _create_error_response(self, error, status_code):
        """Create standardized error response"""
        response = {
            'error': type(error).__name__,
            'message': str(error),
            'status_code': status_code,
            'request_id': g.get('request_id')
        }
        return response, status_code

def request_logger(app):
    """Log request and response details"""
    
    @app.before_request
    def before_request():
        """Log request details"""
        g.start_time = time.time()
        logger.info(
            "Request started",
            extra={
                'method': request.method,
                'path': request.path,
                'ip': request.remote_addr,
                'user_agent': request.user_agent.string,
                'request_id': g.get('request_id')
            }
        )

    @app.after_request
    def after_request(response: Response) -> Response:
        """Log response details"""
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            logger.info(
                "Request completed",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status': response.status_code,
                    'duration': elapsed,
                    'request_id': g.get('request_id')
                }
            )
        return add_cors_headers(response)

def performance_monitor(app):
    """Monitor request performance"""
    
    @app.before_request
    def start_timer():
        g.start = time.time()

    @app.after_request
    def log_performance(response: Response) -> Response:
        """Log slow requests"""
        if hasattr(g, 'start'):
            elapsed = time.time() - g.start
            threshold = app.config.get('SLOW_REQUEST_THRESHOLD', 0.5)
            
            if elapsed > threshold:
                logger.warning(
                    'Slow request detected',
                    extra={
                        'path': request.path,
                        'method': request.method,
                        'duration': elapsed,
                        'request_id': g.get('request_id')
                    }
                )
        return response

def setup_middleware(app):
    """Setup all middleware for the application"""
    # Initialize middleware components
    init_middleware(app)
    
    # Initialize error handler
    error_handler = ErrorHandler()
    error_handler.init_app(app)
    
    # Register request logger
    request_logger(app)
    
    # Register performance monitor
    performance_monitor(app)
    
    # Register CORS handler
    @app.after_request
    def handle_cors(response: Response) -> Response:
        return add_cors_headers(response)
    
    # Register request ID middleware
    @app.before_request
    def add_request_id():
        if 'X-Request-ID' not in request.headers:
            g.request_id = str(uuid.uuid4())
        else:
            g.request_id = request.headers['X-Request-ID']
    
    # Register cleanup middleware
    @app.teardown_request
    def cleanup(exception=None):
        """Cleanup request context"""
        pass  # Add cleanup logic if needed

def require_json(f: Callable) -> Callable:
    """Decorator to require JSON content type"""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not request.is_json:
            raise ValidationError("Content-Type must be application/json")
        return f(*args, **kwargs)
    return decorated_function

def validate_schema(schema: dict):
    """Decorator to validate request against JSON schema"""
    try:
        from jsonschema import validate, ValidationError as JsonSchemaValidationError
    except ImportError:
        raise ImportError("jsonschema package is required for schema validation")
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            if not request.is_json:
                raise ValidationError("Content-Type must be application/json")
            
            try:
                validate(instance=request.json, schema=schema)
            except JsonSchemaValidationError as e:
                raise ValidationError(f"Schema validation failed: {str(e)}")
            except Exception as e:
                raise ValidationError(f"Validation error: {str(e)}")
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Create singleton instance of error handler
error_handler = ErrorHandler()