from enum import StrEnum


class GeneralIntent(StrEnum):
    """General intents (not tied to any specific module)"""
    CHAT = "chat"
    UNKNOWN = "unknown"  # When LLM cannot determine the intent
    
__all__ = ("GeneralIntent",)