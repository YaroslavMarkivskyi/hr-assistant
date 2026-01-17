import logging
from typing import TYPE_CHECKING

from botbuilder.core import ConversationState, MemoryStorage
from botbuilder.azure import BlobsStorage


if TYPE_CHECKING:
    from core.config import Config


logger = logging.getLogger(__name__)


def create_conversation_state(config: "Config") -> ConversationState:
    """
    Create and configure ConversationState with MemoryStorage.
    
    Returns:
        Configured ConversationState instance
    """
    if not config.DEBUG:
        try:
            storage = BlobsStorage(
                container_name=config.AZURE_BLOB_CONTAINER_NAME,
                connection_string=config.AZURE_BLOB_CONNECTION_STRING
            )
            logger.info("Using Azure BlobsStorage for ConversationState")
        except Exception as e:
            logger.error(f"Failed to initialize BlobsStorage: {e}. Falling back to MemoryStorage.", exc_info=True)
            storage = MemoryStorage()
    else:
        storage = MemoryStorage()
        logger.info("Using MemoryStorage for ConversationState (Debug Mode)")
        
    return ConversationState(storage)
    
    
__all__ = ("create_conversation_state",)
