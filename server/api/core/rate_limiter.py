# server/api/core/rate_limiter.py
from typing import Optional, Tuple
import time
from redis import Redis
from flask import request
import logging
from .exceptions import RateLimitError

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter implementation using Redis"""
    
    def __init__(
        self,
        redis_client: Redis,
        limit: int = 100,
        window: int = 60,
        by_ip: bool = True
    ):
        self.redis = redis_client
        self.limit = limit
        self.window = window
        self.by_ip = by_ip
        self.logger = logging.getLogger(__name__)

    def get_identifier(self) -> str:
        """Get identifier for rate limiting"""
        if self.by_ip:
            return request.remote_addr
        return request.headers.get('X-API-Key', request.remote_addr)

    def is_allowed(self, identifier: Optional[str] = None) -> Tuple[bool, dict]:
        """Check if request is allowed"""
        identifier = identifier or self.get_identifier()
        key = f"rate_limit:{identifier}"
        
        try:
            current = time.time()
            pipeline = self.redis.pipeline()
            
            # Clean old requests
            pipeline.zremrangebyscore(key, 0, current - self.window)
            
            # Add current request
            pipeline.zadd(key, {str(current): current})
            
            # Count requests in window
            pipeline.zcard(key)
            
            # Set expiration
            pipeline.expire(key, self.window)
            
            _, _, request_count, _ = pipeline.execute()
            
            remaining = self.limit - request_count
            reset_time = int(current) + self.window
            
            rate_limit_info = {
                'limit': self.limit,
                'remaining': max(0, remaining),
                'reset': reset_time,
                'identifier': identifier
            }
            
            return request_count <= self.limit, rate_limit_info
            
        except Exception as e:
            self.logger.error(f"Rate limiter error: {str(e)}")
            return True, {}

    def __call__(self, f):
        """Decorator implementation"""
        def decorated(*args, **kwargs):
            identifier = self.get_identifier()
            allowed, info = self.is_allowed(identifier)
            
            if not allowed:
                raise RateLimitError(
                    f"Rate limit exceeded for {identifier}. "
                    f"Try again in {info['reset'] - int(time.time())} seconds"
                )

            response = f(*args, **kwargs)
            
            # Add rate limit headers
            response.headers['X-RateLimit-Limit'] = str(self.limit)
            response.headers['X-RateLimit-Remaining'] = str(info.get('remaining', 0))
            response.headers['X-RateLimit-Reset'] = str(info.get('reset', 0))
            
            return response
        return decorated