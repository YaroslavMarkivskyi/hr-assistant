"""
Interfaces (Protocols) for service abstractions

These protocols define contracts that services must implement,
allowing for vendor-agnostic implementations and easy testing.
"""
from .ai_service import AIService

__all__ = ["AIService"]



