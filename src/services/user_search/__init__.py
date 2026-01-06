"""
User Search Service Package

This package provides user search and resolution functionality with:
- Exact and fuzzy name matching
- AI-powered disambiguation
- LRU caching for performance
- Parallel execution for multiple searches

Main entry point: UserSearchService
"""
from .service import UserSearchService
from .types import UserDict, ConfidenceLevel

__all__ = [
    'UserSearchService',
    'UserDict',
    'ConfidenceLevel',
]


