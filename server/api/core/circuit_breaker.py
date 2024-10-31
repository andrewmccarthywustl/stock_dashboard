# server/api/core/circuit_breaker.py
from functools import wraps
import time
from typing import Callable, Any, Dict
import logging
from .exceptions import CircuitBreakerError

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    STATES = ['closed', 'open', 'half_open']
    
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 60,
        half_open_timeout: int = 30,
        excluded_exceptions: tuple = ()
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        self.excluded_exceptions = excluded_exceptions
        self.failures = 0
        self.last_failure_time = 0
        self.state = 'closed'
        self.last_state_change = time.time()
        self.logger = logging.getLogger(__name__)

    def _enter_state(self, new_state: str) -> None:
        """Transition to a new state"""
        self.state = new_state
        self.last_state_change = time.time()
        self.logger.info(f"Circuit breaker entering {new_state} state")

    def _can_try_request(self) -> bool:
        """Determine if a request can be attempted"""
        if self.state == 'closed':
            return True
        
        if self.state == 'open':
            if time.time() - self.last_failure_time >= self.reset_timeout:
                self._enter_state('half_open')
                return True
            return False
            
        if self.state == 'half_open':
            return True
            
        return False

    def _handle_success(self) -> None:
        """Handle successful request"""
        if self.state == 'half_open':
            self._enter_state('closed')
        self.failures = 0

    def _handle_failure(self, exception: Exception) -> None:
        """Handle failed request"""
        if isinstance(exception, self.excluded_exceptions):
            return

        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self._enter_state('open')

    def __call__(self, func: Callable) -> Callable:
        """Decorator implementation"""
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not self._can_try_request():
                raise CircuitBreakerError(
                    f"Circuit breaker is {self.state}. "
                    f"Try again in {self.reset_timeout - (time.time() - self.last_failure_time):.1f} seconds"
                )

            try:
                result = func(*args, **kwargs)
                self._handle_success()
                return result
            except Exception as e:
                self._handle_failure(e)
                raise

        # Add circuit breaker state information to the wrapper
        wrapper.circuit_breaker = self
        return wrapper

    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            'state': self.state,
            'failures': self.failures,
            'last_failure': self.last_failure_time,
            'last_state_change': self.last_state_change
        }

    def reset(self) -> None:
        """Reset circuit breaker to initial state"""
        self.failures = 0
        self.last_failure_time = 0
        self._enter_state('closed')