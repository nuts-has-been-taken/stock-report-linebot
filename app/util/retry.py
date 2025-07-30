"""
Retry utilities with exponential backoff for API calls.
"""
import asyncio
import functools
import random
import time
from typing import Any, Callable, Optional, Tuple, Type, Union

from logger import logger
from .exceptions import YouTubeWorkflowError


def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    max_backoff: float = 60.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator that retries a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor for exponential backoff calculation
        max_backoff: Maximum backoff time in seconds
        jitter: Whether to add random jitter to backoff time
        exceptions: Tuple of exception types to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    # Calculate backoff time
                    backoff_time = min(backoff_factor * (2 ** attempt), max_backoff)
                    if jitter:
                        backoff_time = backoff_time * (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Function {func.__name__} failed on attempt {attempt + 1}, retrying in {backoff_time:.2f}s: {str(e)}")
                    time.sleep(backoff_time)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


async def async_retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    max_backoff: float = 60.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator that retries an async function with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Async function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    # Calculate backoff time
                    backoff_time = min(backoff_factor * (2 ** attempt), max_backoff)
                    if jitter:
                        backoff_time = backoff_time * (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Async function {func.__name__} failed on attempt {attempt + 1}, retrying in {backoff_time:.2f}s: {str(e)}")
                    await asyncio.sleep(backoff_time)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def is_retryable_error(exception: Exception) -> bool:
    """
    Determine if an exception is retryable.
    
    Args:
        exception: The exception to check
        
    Returns:
        True if the exception should trigger a retry, False otherwise
    """
    if isinstance(exception, YouTubeWorkflowError):
        # Don't retry on video not found or permanent errors
        if exception.error_code in ['VIDEO_NOT_FOUND', 'INVALID_CHANNEL', 'QUOTA_EXCEEDED']:
            return False
    
    # Retry on network errors, temporary API issues, etc.
    return True