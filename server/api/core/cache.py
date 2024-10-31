# server/api/core/cache.py
from typing import Any, Optional, Union
import json
from redis import Redis
import logging
from datetime import datetime, timedelta
from .exceptions import CacheError

class CacheService:
    """Service for handling caching operations"""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        self.default_ttl = 300  # 5 minutes

    def _serialize(self, value: Any) -> str:
        """Serialize value to string"""
        try:
            if isinstance(value, (dict, list)):
                return json.dumps(value)
            return str(value)
        except Exception as e:
            self.logger.error(f"Serialization error: {str(e)}")
            raise CacheError(f"Failed to serialize value: {str(e)}")

    def _deserialize(self, value: str) -> Any:
        """Deserialize string to value"""
        try:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            self.logger.error(f"Deserialization error: {str(e)}")
            raise CacheError(f"Failed to deserialize value: {str(e)}")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            return self._deserialize(value)
        except Exception as e:
            self.logger.error(f"Cache get error: {str(e)}")
            raise CacheError(f"Failed to get from cache: {str(e)}")

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        try:
            serialized = self._serialize(value)
            return await self.redis.set(
                key,
                serialized,
                ex=ttl or self.default_ttl
            )
        except Exception as e:
            self.logger.error(f"Cache set error: {str(e)}")
            raise CacheError(f"Failed to set in cache: {str(e)}")

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return await self.redis.delete(key) > 0
        except Exception as e:
            self.logger.error(f"Cache delete error: {str(e)}")
            raise CacheError(f"Failed to delete from cache: {str(e)}")

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            self.logger.error(f"Cache exists error: {str(e)}")
            raise CacheError(f"Failed to check cache existence: {str(e)}")

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment value in cache"""
        try:
            return await self.redis.incr(key, amount)
        except Exception as e:
            self.logger.error(f"Cache increment error: {str(e)}")
            raise CacheError(f"Failed to increment cache value: {str(e)}")

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            self.logger.error(f"Cache expire error: {str(e)}")
            raise CacheError(f"Failed to set cache expiration: {str(e)}")

    def is_healthy(self) -> bool:
        """Check if cache is healthy"""
        try:
            return self.redis.ping()
        except Exception:
            return False

    async def clear_all(self) -> bool:
        """Clear all cache entries"""
        try:
            return await self.redis.flushall()
        except Exception as e:
            self.logger.error(f"Cache clear error: {str(e)}")
            raise CacheError(f"Failed to clear cache: {str(e)}")