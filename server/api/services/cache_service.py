# server/api/services/cache_service.py
from typing import Any, Optional, Union, Dict
import json
from datetime import datetime, timedelta
import logging
from redis import Redis
from ..core.exceptions import CacheError

logger = logging.getLogger(__name__)

class CacheService:
    """Service for handling cache operations with Redis"""
    
    def __init__(self, redis_client: Redis):
        """Initialize cache service with Redis client"""
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Default cache times for different types of data
        self.cache_times = {
            'portfolio': 300,    # 5 minutes
            'positions': 300,    # 5 minutes
            'transactions': 600,  # 10 minutes
            'stock_data': 60,    # 1 minute
            'market_data': 30,   # 30 seconds
            'analytics': 900     # 15 minutes
        }

    def _create_key(self, namespace: str, identifier: str) -> str:
        """Create cache key with namespace"""
        return f"{namespace}:{identifier}"

    def _serialize(self, value: Any) -> str:
        """Serialize value to string"""
        try:
            if isinstance(value, datetime):
                return value.isoformat()
            return json.dumps(value, default=str)
        except Exception as e:
            self.logger.error(f"Serialization error: {str(e)}")
            raise CacheError(f"Failed to serialize value: {str(e)}")

    def _deserialize(self, value: str) -> Any:
        """Deserialize string to value"""
        try:
            data = json.loads(value)
            return data
        except Exception as e:
            self.logger.error(f"Deserialization error: {str(e)}")
            raise CacheError(f"Failed to deserialize value: {str(e)}")

    async def get_portfolio(self, portfolio_id: str) -> Optional[Dict]:
        """Get portfolio from cache"""
        key = self._create_key('portfolio', portfolio_id)
        try:
            data = await self.redis.get(key)
            return self._deserialize(data) if data else None
        except Exception as e:
            self.logger.error(f"Cache get error for portfolio {portfolio_id}: {str(e)}")
            return None

    async def set_portfolio(self, portfolio_id: str, data: Dict) -> bool:
        """Cache portfolio data"""
        key = self._create_key('portfolio', portfolio_id)
        try:
            serialized = self._serialize(data)
            return await self.redis.set(
                key,
                serialized,
                ex=self.cache_times['portfolio']
            )
        except Exception as e:
            self.logger.error(f"Cache set error for portfolio {portfolio_id}: {str(e)}")
            return False

    async def get_position(self, symbol: str, position_type: str) -> Optional[Dict]:
        """Get position from cache"""
        key = self._create_key('position', f"{symbol}:{position_type}")
        try:
            data = await self.redis.get(key)
            return self._deserialize(data) if data else None
        except Exception as e:
            self.logger.error(f"Cache get error for position {symbol}: {str(e)}")
            return None

    async def set_position(
        self,
        symbol: str,
        position_type: str,
        data: Dict
    ) -> bool:
        """Cache position data"""
        key = self._create_key('position', f"{symbol}:{position_type}")
        try:
            serialized = self._serialize(data)
            return await self.redis.set(
                key,
                serialized,
                ex=self.cache_times['positions']
            )
        except Exception as e:
            self.logger.error(f"Cache set error for position {symbol}: {str(e)}")
            return False

    async def get_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get stock data from cache"""
        key = self._create_key('stock', symbol)
        try:
            data = await self.redis.get(key)
            return self._deserialize(data) if data else None
        except Exception as e:
            self.logger.error(f"Cache get error for stock {symbol}: {str(e)}")
            return None

    async def set_stock_data(self, symbol: str, data: Dict) -> bool:
        """Cache stock data"""
        key = self._create_key('stock', symbol)
        try:
            serialized = self._serialize(data)
            return await self.redis.set(
                key,
                serialized,
                ex=self.cache_times['stock_data']
            )
        except Exception as e:
            self.logger.error(f"Cache set error for stock {symbol}: {str(e)}")
            return False

    async def get_analytics(self, key_identifier: str) -> Optional[Dict]:
        """Get analytics data from cache"""
        key = self._create_key('analytics', key_identifier)
        try:
            data = await self.redis.get(key)
            return self._deserialize(data) if data else None
        except Exception as e:
            self.logger.error(f"Cache get error for analytics {key_identifier}: {str(e)}")
            return None

    async def set_analytics(self, key_identifier: str, data: Dict) -> bool:
        """Cache analytics data"""
        key = self._create_key('analytics', key_identifier)
        try:
            serialized = self._serialize(data)
            return await self.redis.set(
                key,
                serialized,
                ex=self.cache_times['analytics']
            )
        except Exception as e:
            self.logger.error(f"Cache set error for analytics {key_identifier}: {str(e)}")
            return False

    async def invalidate_portfolio(self, portfolio_id: str) -> bool:
        """Invalidate portfolio cache"""
        key = self._create_key('portfolio', portfolio_id)
        try:
            return await self.redis.delete(key) > 0
        except Exception as e:
            self.logger.error(f"Cache invalidation error for portfolio {portfolio_id}: {str(e)}")
            return False

    async def invalidate_position(self, symbol: str, position_type: str) -> bool:
        """Invalidate position cache"""
        key = self._create_key('position', f"{symbol}:{position_type}")
        try:
            return await self.redis.delete(key) > 0
        except Exception as e:
            self.logger.error(f"Cache invalidation error for position {symbol}: {str(e)}")
            return False

    async def invalidate_stock_data(self, symbol: str) -> bool:
        """Invalidate stock data cache"""
        key = self._create_key('stock', symbol)
        try:
            return await self.redis.delete(key) > 0
        except Exception as e:
            self.logger.error(f"Cache invalidation error for stock {symbol}: {str(e)}")
            return False

    async def clear_all(self) -> bool:
        """Clear all cache data"""
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            self.logger.error(f"Cache clear error: {str(e)}")
            return False

    def is_healthy(self) -> bool:
        """Check if cache is healthy"""
        try:
            return bool(self.redis.ping())
        except Exception:
            return False

    async def set_with_pattern(
        self,
        pattern: str,
        data: Dict,
        expire_time: Optional[int] = None
    ) -> bool:
        """Set cache with pattern matching"""
        try:
            serialized = self._serialize(data)
            return await self.redis.set(
                pattern,
                serialized,
                ex=expire_time or self.cache_times['portfolio']
            )
        except Exception as e:
            self.logger.error(f"Cache pattern set error: {str(e)}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            self.logger.error(f"Cache pattern invalidation error: {str(e)}")
            return 0

    async def get_multiple(self, keys: list) -> Dict[str, Any]:
        """Get multiple cache entries"""
        try:
            pipe = self.redis.pipeline()
            for key in keys:
                pipe.get(key)
            values = await pipe.execute()
            
            return {
                key: self._deserialize(value) if value else None
                for key, value in zip(keys, values)
            }
        except Exception as e:
            self.logger.error(f"Cache multiple get error: {str(e)}")
            return {}