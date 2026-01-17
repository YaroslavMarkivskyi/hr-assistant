import logging
from dataclasses import dataclass
from botbuilder.core import BotFrameworkAdapter, ConversationState

from bot.adapter import create_adapter
from bot.state import create_conversation_state
from bot.orchestrator import HRBotOrchestrator
from core.containers.service_container import ServiceContainer


logger = logging.getLogger(__name__)

@dataclass
class BotContainer:
    """
    Container for Bot Framework infrastructure components.
    Provides dependency injection for the bot instance, adapter, and conversation state.
    """
    adapter: BotFrameworkAdapter
    conversation_state: ConversationState
    bot: HRBotOrchestrator
    
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
        
        # Initialize adapter
        adapter = create_adapter(service_container.config)
        
        # Initialize conversation state
        # TODO: Pass storage from ServiceContainer if needed
        conversation_state = create_conversation_state(config=service_container.config)
        
        # Initialize bot with service container and conversation state
        bot = HRBotOrchestrator(service_container, conversation_state)
        
        logger.info("BotContainer initialized")
        
        return cls(
            adapter=adapter,
            conversation_state=conversation_state,
            bot=bot
        )



















# import logging
# from dataclasses import dataclass
# from botbuilder.core import BotFrameworkAdapter, ConversationState
# from bot.adapter import create_adapter
# from bot.state import create_conversation_state
# from bot.logic import HRBot
# from core.containers.service_container import ServiceContainer

# logger = logging.getLogger("HRBot")


# @dataclass
# class BotContainer:
#     adapter: BotFrameworkAdapter
#     conversation_state: ConversationState
#     bot: HRBot
    
#     @classmethod
#     def create(cls, service_container: ServiceContainer) -> 'BotContainer':
#         """
#         Factory method to create BotContainer with initialized infrastructure.
        
#         This method:
#         1. Creates BotFrameworkAdapter (with Single Tenant configuration)
#         2. Initializes ConversationState
#         3. Creates HRBot instance with ServiceContainer
        
#         Args:
#             service_container: ServiceContainer with business services
            
#         Returns:
#             BotContainer with all infrastructure components initialized
#         """
#         logger.info("🚀 Initializing Bot Framework infrastructure...")
        
#         # Initialize adapter (with Single Tenant configuration)
#         adapter = create_adapter()
        
#         # Initialize conversation state
#         conversation_state = create_conversation_state()
        
#         # Initialize bot with service container and conversation state
#         # ConversationState is required for state persistence (save_changes)
#         bot = HRBot(service_container, conversation_state)
        
#         logger.info("✅ BotContainer initialized")
        
#         return cls(
#             adapter=adapter,
#             conversation_state=conversation_state,
#             bot=bot
#         )

