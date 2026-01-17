"""
Bot State Management

Handles conversation state and memory storage initialization.
"""
from botbuilder.core import ConversationState, MemoryStorage
import logging

logger = logging.getLogger("HRBot")


def create_conversation_state() -> ConversationState:
    """
    Create and configure ConversationState with MemoryStorage.
    
    Returns:
        Configured ConversationState instance
    """
    memory = MemoryStorage()
    conversation_state = ConversationState(memory)
    logger.info("ConversationState initialized")
    return conversation_state

