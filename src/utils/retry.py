"""
Retry Decorator for External API Calls

Provides a reusable retry mechanism with exponential backoff for rate limits.
Can be applied to any async function that calls external APIs (OpenAI, Database, etc.).

Usage:
    @retry_with_backoff(max_retries=2, base_delay=1.0)
    async def my_api_call():
        # Your API call here
        pass
"""
import asyncio
import logging
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

logger = logging.getLogger("HRBot")

P = ParamSpec('P')
T = TypeVar('T')


def _is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is retryable (transient network/API issues).
    
    Retryable errors:
    - Connection errors (network issues)
    - Timeout errors
    - HTTP 5xx errors (server errors)
    - HTTP 429 (Rate Limit) - CRITICAL: Must retry with backoff
    
    Non-retryable errors:
    - HTTP 4xx errors (except 429): client errors, bad API key, etc.
    - Authentication errors (401, 403)
    - Validation errors (400)
    
    Args:
        error: Exception to check
        
    Returns:
        True if error is retryable, False otherwise
    """
    error_str = str(error).lower()
    error_type = type(error).__name__.lower()
    
    # Rate limit (429) - CRITICAL: Must retry with exponential backoff
    if "429" in error_str or "rate limit" in error_str or "too many requests" in error_str:
        return True
    
    # Network/connection errors - retryable
    if any(keyword in error_type or keyword in error_str for keyword in [
        "timeout", "connection", "network", "unreachable", 
        "refused", "reset", "broken", "500", "502", "503", "504"
    ]):
        return True
    
    # Client errors (4xx, except 429) - not retryable
    if any(keyword in error_str for keyword in ["400", "401", "403", "404"]):
        return False
    
    # Default: retry for unknown errors (might be transient)
    return True


def _get_retry_delay(error: Exception, base_delay: float, attempt: int) -> float:
    """
    Calculate retry delay with exponential backoff for rate limit errors.
    
    For 429 (Rate Limit) errors, uses exponential backoff:
    - Attempt 0: base_delay * 2^1 = 2.0s
    - Attempt 1: base_delay * 2^2 = 4.0s
    - Attempt 2: base_delay * 2^3 = 8.0s
    
    For other retryable errors, uses base delay.
    
    Args:
        error: Exception that triggered the retry
        base_delay: Base delay in seconds
        attempt: Current attempt number (0-indexed)
        
    Returns:
        Delay in seconds before next retry
    """
    error_str = str(error).lower()
    
    # Exponential backoff for rate limit errors
    if "429" in error_str or "rate limit" in error_str or "too many requests" in error_str:
        # Exponential backoff: base_delay * 2^(attempt + 1)
        exponential_delay = base_delay * (2 ** (attempt + 1))
        logger.info(f"⏳ Rate limit detected, using exponential backoff: {exponential_delay:.1f}s")
        return exponential_delay
    
    # For other errors, use base delay
    return base_delay


def retry_with_backoff(
    max_retries: int = 2,
    base_delay: float = 1.0,
    log_attempts: bool = True
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator for retrying async functions with exponential backoff.
    
    This decorator handles:
    - Retry logic for transient errors (timeouts, network issues, rate limits)
    - Exponential backoff for rate limit errors (429)
    - Logging of retry attempts
    - Proper exception propagation for non-retryable errors
    
    Args:
        max_retries: Maximum number of retry attempts (default: 2)
        base_delay: Base delay in seconds between retries (default: 1.0)
        log_attempts: Whether to log retry attempts (default: True)
        
    Returns:
        Decorated function with retry logic
        
    Example:
        @retry_with_backoff(max_retries=3, base_delay=1.5)
        async def call_openai_api():
            # Your API call
            pass
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except asyncio.TimeoutError as e:
                    last_error = e
                    if log_attempts:
                        logger.warning(
                            f"⏱️ Timeout in {func.__name__} "
                            f"(attempt {attempt + 1}/{max_retries + 1}): {e}"
                        )
                    if attempt < max_retries:
                        await asyncio.sleep(base_delay)
                        continue
                    else:
                        if log_attempts:
                            logger.error(
                                f"❌ {func.__name__} timeout after {max_retries + 1} attempts"
                            )
                        raise
                        
                except Exception as e:
                    last_error = e
                    error_type = type(e).__name__
                    
                    if log_attempts:
                        logger.warning(
                            f"⚠️ Error in {func.__name__} ({error_type}, "
                            f"attempt {attempt + 1}/{max_retries + 1}): {e}"
                        )
                    
                    # Retry only for network/transient errors
                    if attempt < max_retries and _is_retryable_error(e):
                        delay = _get_retry_delay(e, base_delay, attempt)
                        await asyncio.sleep(delay)
                        continue
                    else:
                        if log_attempts:
                            logger.error(
                                f"❌ {func.__name__} failed after {attempt + 1} attempt(s): {error_type}"
                            )
                        raise
            
            # This should never be reached, but just in case
            if last_error:
                raise last_error
            raise RuntimeError(f"{func.__name__} failed after {max_retries + 1} attempts")
        
        return wrapper
    return decorator

