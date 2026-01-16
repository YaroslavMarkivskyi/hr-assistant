"""
Bot Container - Infrastructure Container

Manages Bot Framework infrastructure components:
- BotFrameworkAdapter
- ConversationState
- HRBot instance

This follows the Composition Root pattern, separating bot infrastructure
from business logic (ServiceContainer) and application entry point (main.py).
"""
import logging
from dataclasses import dataclass
from botbuilder.core import BotFrameworkAdapter, ConversationState
from bot.adapter import create_adapter
from bot.state import create_conversation_state
from bot.logic import HRBot
from core.containers.service_container import ServiceContainer

logger = logging.getLogger("HRBot")


@dataclass
class BotContainer:
    """
    Container for Bot Framework infrastructure components.
    
    Responsibilities:
    - Bot Framework Adapter (authentication, message processing)
    - Conversation State (memory management)
    - Bot instance (business logic handler)
    
    This container is separate from ServiceContainer, which handles
    business services (Graph API, Database, OpenAI, Email).
    """
    adapter: BotFrameworkAdapter
    conversation_state: ConversationState
    bot: HRBot
    
    @classmethod
    def create(cls, service_container: ServiceContainer) -> 'BotContainer':
        """
        Factory method to create BotContainer with initialized infrastructure.
        
        This method:
        1. Creates BotFrameworkAdapter (with Single Tenant configuration)
        2. Initializes ConversationState
        3. Creates HRBot instance with ServiceContainer
        
        Args:
            service_container: ServiceContainer with business services
            
        Returns:
            BotContainer with all infrastructure components initialized
        """
        logger.info("🚀 Initializing Bot Framework infrastructure...")
        
        # Initialize adapter (with Single Tenant configuration)
        adapter = create_adapter()
        
        # Initialize conversation state
        conversation_state = create_conversation_state()
        
        # Initialize bot with service container and conversation state
        # ConversationState is required for state persistence (save_changes)
        bot = HRBot(service_container, conversation_state)
        
        logger.info("✅ BotContainer initialized")
        
        return cls(
            adapter=adapter,
            conversation_state=conversation_state,
            bot=bot
        )

