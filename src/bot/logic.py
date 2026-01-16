"""
Bot Business Logic

Contains the core bot logic for handling messages.
This module is isolated from infrastructure concerns (adapter, FastAPI, etc.).
"""
import logging
from botbuilder.core import TurnContext, ConversationState
from botbuilder.schema import ActivityTypes
from bot.activity_context_wrapper import ActivityContextWrapper
from bot.router import MessageRouter
from core.containers.service_container import ServiceContainer
from utils.helpers import get_user_language
from resources import get_translation
from enums.translation_key import TranslationKey

logger = logging.getLogger("HRBot")


class HRBot:
    """
    Main bot class that handles incoming messages.
    
    This class only knows about:
    - TurnContext (from Bot Framework)
    - ConversationState (for state persistence)
    - ServiceContainer (dependency injection)
    - Router logic (route_message)
    
    It does NOT know about:
    - FastAPI
    - Azure authentication
    - Tenant IDs
    - Adapter configuration
    """
    
    def __init__(
        self, 
        service_container: ServiceContainer,
        conversation_state: ConversationState
    ):
        """
        Initialize HRBot with service container and conversation state.
        
        Args:
            service_container: Container with all bot services
            conversation_state: Conversation state for persistence
        """
        self.container = service_container
        self.conversation_state = conversation_state
    
    async def on_turn(self, turn_context: TurnContext) -> None:
        """
        Handle incoming turn from Bot Framework.
        
        This method:
        1. Routes the message to appropriate handler
        2. Saves conversation state after processing (CRITICAL for state persistence)
        
        Args:
            turn_context: Bot Framework turn context
        """
        # Create ActivityContext wrapper from TurnContext (required by router and localization)
        # This adapts TurnContext to ActivityContext API
        ctx = ActivityContextWrapper(turn_context)
        
        try:
            # Route message to appropriate handler
            router = MessageRouter(ctx, self.container)
            await router.route()
            
        except Exception as e:
            logger.error(f"❌ Error in HRBot.on_turn: {e}", exc_info=True)
            
            # Send localized error message to user
            if turn_context.activity.type == ActivityTypes.message:
                # Get user language for localized error message
                language = get_user_language(ctx)
                error_message = get_translation(
                    TranslationKey.MESSAGE_PROCESSING_ERROR, 
                    language
                    )
                await turn_context.send_activity(error_message)
        
        finally:
            # CRITICAL: Save conversation state after processing (always, even on error)
            # Without this, any state changes (e.g., dialog step, user data) will be lost
            # Using finally ensures state is saved regardless of success or failure
            try:
                await self.conversation_state.save_changes(turn_context)
            except Exception as save_error:
                logger.error(f"❌ Failed to save state: {save_error}", exc_info=True)

