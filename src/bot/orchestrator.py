
import logging

from botbuilder.core import TurnContext, ConversationState
from botbuilder.schema import ActivityTypes

from core.containers.service_container import ServiceContainer
from core.enums.translation_key import TranslationKey

from bot.activity_context_wrapper import ActivityContextWrapper

from utils.helpers import get_user_language
from resources import get_translation


logger = logging.getLogger(__name__)


class HRBotOrchestrator:
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
        self._container = service_container
        self._conversation_state = conversation_state

    async def on_turn(self, turn_context: TurnContext) -> None:
        """
        Handle incoming turn from Bot Framework.
        This method:
        1. Wraps TurnContext to ActivityContextWrapper
        2. Routes the message to appropriate handler via dispatcher
        3. Saves conversation state after processing (CRITICAL for state persistence)
        Args:
            turn_context: Bot Framework turn context
        """
        
        ctx = ActivityContextWrapper(turn_context)
        
        try:
            request = await self._container.classifier.classify(turn_context)
            await self._container.dispatcher.dispatch(
                ctx=ctx,
                request=request,
                container=self._container
            )
        except Exception as e:
            logger.error(f"Error in HRBotOrchestrator.on_turn: {e}", exc_info=True)
            await self._handle_error(turn_context, ctx)
        finally:
            await self._conversation_state.save_changes(turn_context)
            
    async def _handle_error(self, turn_context: TurnContext, ctx: ActivityContextWrapper) -> None:
        """Handle errors by sending localized message to user."""
        if turn_context.activity.type == ActivityTypes.message:
            language = get_user_language(ctx)
            error_message = get_translation(
                TranslationKey.MESSAGE_PROCESSING_ERROR, 
                language
            )
            await turn_context.send_activity(error_message)


# class HRBot:
#     """
#     Main bot class that handles incoming messages.
    
#     This class only knows about:
#     - TurnContext (from Bot Framework)
#     - ConversationState (for state persistence)
#     - ServiceContainer (dependency injection)
#     - Router logic (route_message)
    
#     It does NOT know about:
#     - FastAPI
#     - Azure authentication
#     - Tenant IDs
#     - Adapter configuration
#     """
    
#     def __init__(
#         self, 
#         service_container: ServiceContainer,
#         conversation_state: ConversationState
#     ):
#         """
#         Initialize HRBot with service container and conversation state.
        
#         Args:
#             service_container: Container with all bot services
#             conversation_state: Conversation state for persistence
#         """
#         self.container = service_container
#         self.conversation_state = conversation_state
    
#     async def on_turn(self, turn_context: TurnContext) -> None:
#         """
#         Handle incoming turn from Bot Framework.
        
#         This method:
#         1. Routes the message to appropriate handler
#         2. Saves conversation state after processing (CRITICAL for state persistence)
        
#         Args:
#             turn_context: Bot Framework turn context
#         """
#         # Create ActivityContext wrapper from TurnContext (required by router and localization)
#         # This adapts TurnContext to ActivityContext API
#         ctx = ActivityContextWrapper(turn_context)
        
#         try:
#             # Route message to appropriate handler
#             router = MessageRouter(ctx, self.container)
#             await router.route()
            
#         except Exception as e:
#             logger.error(f"Error in HRBot.on_turn: {e}", exc_info=True)
            
#             # Send localized error message to user
#             if turn_context.activity.type == ActivityTypes.message:
#                 # Get user language for localized error message
#                 language = get_user_language(ctx)
#                 error_message = get_translation(
#                     TranslationKey.MESSAGE_PROCESSING_ERROR, 
#                     language
#                     )
#                 await turn_context.send_activity(error_message)
        
#         finally:
#             # CRITICAL: Save conversation state after processing (always, even on error)
#             # Without this, any state changes (e.g., dialog step, user data) will be lost
#             # Using finally ensures state is saved regardless of success or failure
#             try:
#                 await self.conversation_state.save_changes(turn_context)
#             except Exception as save_error:
#                 logger.error(f"Failed to save state: {save_error}", exc_info=True)

