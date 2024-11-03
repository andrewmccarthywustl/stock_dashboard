import time
from functools import wraps
from typing import Any, Callable, TypeVar, ParamSpec

P = ParamSpec("P")
T = TypeVar("T")

class APIError(Exception):
    """Custom exception for API errors"""
    pass

def retry_on_failure(
    max_retries: int = 3,
    delay: int = 1,
    exceptions: tuple = (Exception,)
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to retry failed operations with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Base delay between retries (will be multiplied by 2^retry_count)
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception = None
            for retry in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if retry < max_retries - 1:
                        sleep_time = delay * (2 ** retry)  # Exponential backoff
                        time.sleep(sleep_time)
                    continue
            raise last_exception
        return wrapper
    return decorator

def format_currency(value: float) -> str:
    """Format a number as currency"""
    return f"${value:,.2f}"

def validate_required_fields(data: dict, required_fields: list) -> None:
    """Validate that all required fields are present in the data"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")