# server/api/core/connection_pool.py
from typing import Dict, Any, Optional
import threading
import queue
import time
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Connection:
    """Base connection class"""
    def __init__(self, **kwargs):
        self.params = kwargs
        self.created_at = time.time()
        self.last_used = self.created_at
        self.is_closed = False

    def close(self):
        """Close the connection"""
        self.is_closed = True

    def is_expired(self, max_age: int) -> bool:
        """Check if connection is expired"""
        return time.time() - self.created_at > max_age

    def is_idle(self, idle_timeout: int) -> bool:
        """Check if connection is idle"""
        return time.time() - self.last_used > idle_timeout

class ConnectionPool:
    """Thread-safe connection pool"""
    
    def __init__(
        self,
        max_size: int = 10,
        min_size: int = 2,
        max_age: int = 3600,
        idle_timeout: int = 300,
        **connection_params
    ):
        """
        Initialize connection pool
        
        Args:
            max_size: Maximum number of connections
            min_size: Minimum number of connections
            max_age: Maximum age of connection in seconds
            idle_timeout: Idle timeout in seconds
            connection_params: Parameters for creating connections
        """
        self.max_size = max_size
        self.min_size = min_size
        self.max_age = max_age
        self.idle_timeout = idle_timeout
        self.connection_params = connection_params
        
        self.pool = queue.Queue(maxsize=max_size)
        self.size = 0
        self._lock = threading.Lock()
        self._maintain_timer = None
        
        # Initialize minimum connections
        self._initialize_pool()
        
        # Start maintenance thread
        self._start_maintenance()

    def _initialize_pool(self) -> None:
        """Initialize pool with minimum connections"""
        for _ in range(self.min_size):
            self._add_connection()

    def _add_connection(self) -> None:
        """Add a new connection to the pool"""
        with self._lock:
            if self.size < self.max_size:
                try:
                    conn = Connection(**self.connection_params)
                    self.pool.put(conn)
                    self.size += 1
                except Exception as e:
                    logger.error(f"Error creating connection: {str(e)}")
                    raise

    def _maintain_pool(self) -> None:
        """Maintain pool size and remove expired connections"""
        try:
            # Remove expired connections
            with self._lock:
                active_connections = []
                while not self.pool.empty():
                    conn = self.pool.get()
                    if (not conn.is_closed and
                        not conn.is_expired(self.max_age) and
                        not conn.is_idle(self.idle_timeout)):
                        active_connections.append(conn)
                    else:
                        conn.close()
                        self.size -= 1

                # Return active connections to pool
                for conn in active_connections:
                    self.pool.put(conn)

            # Ensure minimum connections
            while self.size < self.min_size:
                self._add_connection()
                
        except Exception as e:
            logger.error(f"Error maintaining pool: {str(e)}")
        finally:
            # Schedule next maintenance
            self._maintain_timer = threading.Timer(60, self._maintain_pool)
            self._maintain_timer.daemon = True
            self._maintain_timer.start()

    def _start_maintenance(self) -> None:
        """Start maintenance thread"""
        self._maintain_timer = threading.Timer(60, self._maintain_pool)
        self._maintain_timer.daemon = True
        self._maintain_timer.start()

    @contextmanager
    def get_connection(self, timeout: Optional[float] = None):
        """Get a connection from the pool"""
        conn = None
        try:
            conn = self.pool.get(timeout=timeout)
            conn.last_used = time.time()
            yield conn
        finally:
            if conn and not conn.is_closed:
                self.pool.put(conn)

    def close_all(self) -> None:
        """Close all connections"""
        if self._maintain_timer:
            self._maintain_timer.cancel()
            
        with self._lock:
            while not self.pool.empty():
                conn = self.pool.get()
                conn.close()
            self.size = 0