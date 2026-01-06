"""
General Module Controller

Level 2 dispatcher: Handles general intents (chat, unknown) that don't belong to any specific module.
"""
import logging
from typing import Dict, Callable, Awaitable

from bot.activity_context_wrapper import ActivityContextWrapper
from enums.bot import GeneralIntent, AnyIntent
from enums.translation_key import TranslationKey
from container import ServiceContainer
from handlers.base import BaseModuleController
from handlers.registry import register_controller, GENERAL_MODULE
from models.action import ActionPayload
from models.ai import AIResponse

logger = logging.getLogger("HRBot")

# Type alias for handler functions
GeneralIntentHandler = Callable[
    [ActivityContextWrapper, str, AIResponse, ServiceContainer],
    Awaitable[None]
]


@register_controller(GENERAL_MODULE)
class GeneralController(BaseModuleController):
    """
    Controller for General intents (chat, unknown).
    
    Handles intents that don't belong to any specific domain module.
    """
    
    def __init__(self, service: None) -> None:
        """Initialize controller with route map."""
        super().__init__(service)
        # Intent route map: GeneralIntent -> handler function
        self._intent_handlers: Dict[GeneralIntent, GeneralIntentHandler] = {
            GeneralIntent.CHAT: self._handle_chat,
            GeneralIntent.UNKNOWN: self._handle_unknown,
        }
    
    async def handle_intent(
        self,
        ctx: ActivityContextWrapper,
        intent: str,
        ai_response: AIResponse,
        container: ServiceContainer
    ) -> None:
        """
        Handles general intents (chat, unknown).
        
        Args:
            ctx: Activity context wrapper
            intent: Intent string ("chat" or "unknown")
            ai_response: Validated AIResponse from AI service
            container: Service container with all services
        """
        try:
            general_intent = GeneralIntent(intent)
        except ValueError:
            logger.warning(f"⚠️ Invalid General intent: {intent}, treating as UNKNOWN")
            general_intent = GeneralIntent.UNKNOWN
        
        handler = self._intent_handlers.get(general_intent, self._handle_unknown)
        await handler(ctx, intent, ai_response, container)
    
    async def handle_action(
        self,
        ctx: ActivityContextWrapper,
        payload: ActionPayload,
        container: ServiceContainer
    ) -> None:
        """
        General module doesn't handle actions.
        
        This method exists to satisfy ModuleController protocol.
        """
        logger.warning(
            f"⚠️ General module received action '{payload.action.value}' - "
            f"actions should be handled by domain modules"
        )
        await self._send_unhandled_request(ctx)
    
    async def _handle_chat(
        self,
        ctx: ActivityContextWrapper,
        intent: str,  # pylint: disable=unused-argument
        ai_response: AIResponse,  # pylint: disable=unused-argument
        container: ServiceContainer  # pylint: disable=unused-argument
    ) -> None:
        """Handles chat intent - shows bot capabilities."""
        # Build message with Scheduling capabilities using localized strings
        message_parts = [
            self._get_translation(ctx, TranslationKey.MESSAGE_CHAT_GREETING),
            self._get_translation(ctx, TranslationKey.MESSAGE_CHAT_SCHEDULING_CAPABILITIES),
            self._get_translation(ctx, TranslationKey.MESSAGE_CHAT_FOOTER),
        ]
        
        message = "\n".join(message_parts)
        await ctx.send_activity(message)
    
    async def _handle_unknown(
        self,
        ctx: ActivityContextWrapper,
        intent: str,  # pylint: disable=unused-argument
        ai_response: AIResponse,  # pylint: disable=unused-argument
        container: ServiceContainer  # pylint: disable=unused-argument
    ) -> None:
        """Handles unknown intent - shows help message."""
        await self._send_localized(ctx, TranslationKey.MESSAGE_UNKNOWN_INTENT)

