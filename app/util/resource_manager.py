"""
Resource management utilities for database connections and external API clients.
"""
import contextlib
import functools
import threading
from typing import Any, Callable, Generator, Optional
from sqlalchemy.orm import Session

from app.core.config import postgress_db
from logger import logger


class DatabaseConnectionManager:
    """Thread-safe database connection manager with connection pooling."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.Session = postgress_db.SESSION
            self.initialized = True
    
    @contextlib.contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic cleanup.
        
        Yields:
            SQLAlchemy session instance
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()


def with_db_session(func: Callable) -> Callable:
    """
    Decorator to automatically inject database session into function.
    
    The decorated function should accept a 'session' parameter.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db_manager = DatabaseConnectionManager()
        with db_manager.get_session() as session:
            return func(*args, session=session, **kwargs)
    return wrapper


class APIRateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls: int = 100, time_window: int = 3600):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self._lock = threading.Lock()
    
    def can_make_call(self) -> bool:
        """Check if a new API call can be made within rate limits."""
        import time
        
        with self._lock:
            now = time.time()
            # Remove calls outside the time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False
    
    def wait_time(self) -> float:
        """Get the time to wait before next call can be made."""
        import time
        
        with self._lock:
            if not self.calls:
                return 0.0
            
            oldest_call = min(self.calls)
            time_passed = time.time() - oldest_call
            return max(0, self.time_window - time_passed)


# Global rate limiters for different APIs
youtube_rate_limiter = APIRateLimiter(max_calls=100, time_window=3600)  # 100 calls per hour
openai_rate_limiter = APIRateLimiter(max_calls=50, time_window=60)      # 50 calls per minute


def rate_limited(limiter: APIRateLimiter):
    """
    Decorator to apply rate limiting to API calls.
    
    Args:
        limiter: The rate limiter instance to use
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            while not limiter.can_make_call():
                wait_time = limiter.wait_time()
                if wait_time > 0:
                    logger.info(f"Rate limit reached for {func.__name__}, waiting {wait_time:.2f}s")
                    time.sleep(min(wait_time, 60))  # Wait max 1 minute at a time
                
            return func(*args, **kwargs)
        return wrapper
    return decorator


@contextlib.contextmanager
def temporary_file_cleanup(*file_paths: str) -> Generator[None, None, None]:
    """
    Context manager to ensure temporary files are cleaned up.
    
    Args:
        *file_paths: Paths to temporary files that should be cleaned up
    """
    import os
    
    try:
        yield
    finally:
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.debug(f"Cleaned up temporary file: {file_path}")
                except OSError as e:
                    logger.warning(f"Failed to clean up temporary file {file_path}: {e}")


class CircuitBreaker:
    """Circuit breaker pattern for API calls."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
    
    def can_execute(self) -> bool:
        """Check if function execution is allowed."""
        import time
        
        with self._lock:
            if self.state == 'CLOSED':
                return True
            elif self.state == 'OPEN':
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                    return True
                return False
            else:  # HALF_OPEN
                return True
    
    def record_success(self):
        """Record a successful execution."""
        with self._lock:
            self.failure_count = 0
            self.state = 'CLOSED'
    
    def record_failure(self):
        """Record a failed execution."""
        import time
        
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures")


def circuit_breaker(breaker: CircuitBreaker):
    """
    Decorator to apply circuit breaker pattern to functions.
    
    Args:
        breaker: The circuit breaker instance to use
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not breaker.can_execute():
                raise Exception(f"Circuit breaker is open for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                raise
        return wrapper
    return decorator