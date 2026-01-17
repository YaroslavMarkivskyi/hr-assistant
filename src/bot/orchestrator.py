
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

__all__ = (
    "HRBotOrchestrator",
)

