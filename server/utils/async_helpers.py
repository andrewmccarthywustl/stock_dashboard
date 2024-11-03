# server/api/utils/async_helpers.py
import asyncio
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

def async_route(f: Callable) -> Callable:
    """Decorator to handle async route functions"""
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(f(*args, **kwargs))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Async route error: {str(e)}")
            raise
    return wrapper

async def run_in_threadpool(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """Run a blocking function in a threadpool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

class AsyncLock:
    """Context manager for async locks"""
    def __init__(self):
        self._lock = asyncio.Lock()
        
    async def __aenter__(self):
        await self._lock.acquire()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()