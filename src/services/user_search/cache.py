"""
LRU Cache implementation for user search results.

This module provides a simple LRU cache with TTL for caching search results.
"""
import time
from collections import OrderedDict
from typing import Any, Optional, Tuple

# Cache configuration
CACHE_TTL_SECONDS = 300  # 5 minutes
CACHE_MAX_SIZE = 1000  # Maximum number of cached entries


class LRUCache:
    """
    Simple LRU cache with TTL for search results.
    
    Thread-safe for async operations (single-threaded event loop).
    """
    
    def __init__(self, max_size: int = CACHE_MAX_SIZE, ttl: int = CACHE_TTL_SECONDS):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of entries in cache
            ttl: Time to live in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        
        # Check if expired
        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Remove oldest
        
        self.cache[key] = (value, time.time())
        self.cache.move_to_end(key)
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()


