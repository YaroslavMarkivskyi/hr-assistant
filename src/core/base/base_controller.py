from __future__ import annotations

import logging
from abc import ABC
from typing import TYPE_CHECKING, Union, Optional

from core.enums.translation_key import TranslationKey
from core.utils.helpers import get_user_language

from resources import get_translation   

from handlers.utils import get_requester_id


if TYPE_CHECKING:
    from core.containers.service_container import ServiceContainer
    from bot.activity_context_wrapper import ActivityContextWrapper
    from schemas.bot import ActionPayload, IntentPayload
    

logger = logging.getLogger(__name__)


class BaseController(ABC):
    """
    Abstract base class for all module controllers.
    Defines the interface for handling actions and intents.
    """
    def __init__(self, container: "ServiceContainer") -> None:
        self._container = container

    async def handle_action(
        self,
        ctx: "ActivityContextWrapper",
        payload: ActionPayload,
    ) -> None:
        """
        Handle an action (button click) from the user.
        """
        method_name = f"handle_action_{payload.action.name.lower()}"
        await self._execute_handler(method_name, ctx, payload)

    async def handle_intent(
        self,
        ctx: "ActivityContextWrapper",
        payload: IntentPayload,
    ) -> None:
        """
        Handle an intent recognized from user input.
        """
        method_name = f"handle_intent_{payload.intent.name.lower()}"
        await self._execute_handler(method_name, ctx, payload)
        
    async def _execute_handler(
        self,
        method_name: str,
        ctx: "ActivityContextWrapper",
        payload: Union[ActionPayload, IntentPayload],
    ) -> None:
        """
        Execute the handler method if it exists, otherwise log an error.
        """
        handler = getattr(self, method_name, None)
        
        if callable(handler):
            try:
                await handler(ctx, payload)
            except Exception as e:
                logger.error(f"Error executing {method_name}: {e}", exc_info=True)
                # TODO: Add error handling logic (e.g., notify user)
                raise
        else:
            logger.error(f"Handler method {method_name} not implemented in {self.__class__.__name__}.")
            await self._send_unhandled_request(ctx)

            
    async def _get_requester_id_or_error(
        self,
        ctx: "ActivityContextWrapper",
    ) -> Optional[str]:
        """
        Retrieve the requester ID from the context or send an error message if not found.
        """
        requester_id = get_requester_id(ctx, self._container.config)
        if not requester_id:
            await self._send_error(
                ctx,
                TranslationKey.MESSAGE_USER_IDENTIFICATION_ERROR
            )
            return None
        return requester_id
            
    async def _send_localized(
        self,
        ctx: "ActivityContextWrapper",
        translation_key: TranslationKey,
        **kwargs
    ) -> None:
        """
        Sends a localized message to the user with optional formatting.
        
        Args:
            ctx: Activity context wrapper
            translation_key: Translation key for the message
            **kwargs: Variables to format into the translation string
            
        Example:
            >>> await self._send_localized(ctx, TranslationKey.MESSAGE_GREETING, user_name="Alice")
            # Sends formatted greeting message with the user's name
        """
        language = get_user_language(ctx)
        template = get_translation(translation_key, language)
        message = template.format(**kwargs) if kwargs else template
        await ctx.send_activity(message)
        
    async def _send_error(
        self,
        ctx: "ActivityContextWrapper",
        translation_key: TranslationKey,
        **kwargs
    ) -> None:
        """
        Sends a localized error message to the user with optional formatting.
        
        This is a convenience wrapper around _send_localized for semantic clarity.
        
        Args:
            ctx: Activity context wrapper
            translation_key: Translation key for the error message
            **kwargs: Variables to format into the translation string
            
        Example:
            >>> await self._send_error(ctx, TranslationKey.MESSAGE_PROCESSING_ERROR, error="Database connection failed")
            # Sends formatted error message with the error details
        """
        await self._send_localized(ctx, translation_key, **kwargs)
    
    async def _send_unhandled_request(
        self,
        ctx: "ActivityContextWrapper"
    ) -> None:
        """
        Sends a localized "unhandled request" message to the user.
        
        Args:
            ctx: Activity context wrapper
        """
        await self._send_error(ctx, TranslationKey.MESSAGE_UNHANDLED_REQUEST)


__all__ = (
    'BaseController',
)

