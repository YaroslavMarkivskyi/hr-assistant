from __future__ import annotations

import logging
from abc import ABC
from typing import TYPE_CHECKING, Union


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

            
__all__ = (
    'BaseController',
)

