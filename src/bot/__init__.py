"""
Bot module - core bot logic and infrastructure
"""
from .adapter import create_adapter
from .orchestrator import HRBot
from .state import create_conversation_state
from .router import MessageRouter

__all__ = ["create_adapter", "HRBot", "create_conversation_state", "MessageRouter"]

