# server/api/core/exceptions.py
class APIError(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

class ValidationError(APIError):
    """Raised when request validation fails"""
    def __init__(self, message: str):
        super().__init__(message, 400)

class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, 429)

class CircuitBreakerError(APIError):
    """Raised when circuit breaker is open"""
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, 503)

class CacheError(APIError):
    """Raised when cache operations fail"""
    def __init__(self, message: str):
        super().__init__(message, 500)

class DatabaseError(APIError):
    """Raised when database operations fail"""
    def __init__(self, message: str):
        super().__init__(message, 500)

class ExternalServiceError(APIError):
    """Raised when external service calls fail"""
    def __init__(self, message: str):
        super().__init__(message, 502)

class AuthenticationError(APIError):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)

class AuthorizationError(APIError):
    """Raised when authorization fails"""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, 403)

class ResourceNotFoundError(APIError):
    """Raised when requested resource is not found"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)

class ConflictError(APIError):
    """Raised when there's a conflict with existing resource"""
    def __init__(self, message: str):
        super().__init__(message, 409)