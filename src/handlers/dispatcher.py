import logging
from typing import TYPE_CHECKING, Optional, Callable, Union, Awaitable, Dict

from core.enums.bot import (
    BotModule,
    BotRequestType,
    get_module_for_action,
    get_module_for_intent
)
from core.enums.translation_key import TranslationKey
from core.utils.helpers import get_user_language
from core.base import BaseController

from schemas.bot import ActionPayload, IntentPayload

from resources import get_translation


if TYPE_CHECKING:
    from bot.activity_context_wrapper import ActivityContextWrapper
    from core.containers.service_container import ServiceContainer
    from schemas.bot import ClassifiedRequest
    

logger = logging.getLogger(__name__)


HandlerType = Callable[
    ["ActivityContextWrapper", Union[ActionPayload, IntentPayload], "ServiceContainer"],
    Awaitable[None]
]


class BotDispatcher:

    def __init__(self) -> None:
        self._handlers: Dict[BotRequestType, HandlerType] = {
            BotRequestType.ACTION: self._dispatch_action,
            BotRequestType.INTENT: self._dispatch_intent,
        }
    
    async def dispatch(
        self,
        ctx: "ActivityContextWrapper",
        request: "ClassifiedRequest",
        container: "ServiceContainer"
    ) -> None:
        """
        Level 1 dispatcher: Routes messages to module controllers.
        """
        handler = self._handlers.get(request.request_type, self._handle_unknown_type)
        await handler(ctx, request.payload, container)
            
    async def _dispatch_action(
        self,
        ctx: "ActivityContextWrapper",
        payload: ActionPayload,
        container: "ServiceContainer"
    ) -> None:
        """
        Level 1: Routes action (button click) to appropriate module controller.
        """
        await self._process_routing(
            ctx=ctx,
            container=container,
            payload=payload,
            module_key=get_module_for_action(payload.action),
            handle_method="handle_action",
            log_label="ACTION"
        )
        
            
    async def _dispatch_intent(
        self,
        ctx: "ActivityContextWrapper",
        payload: IntentPayload,
        container: "ServiceContainer"
    ) -> None:
        """
        Level 1: Routes AI intent to appropriate module controller.
        """
        await self._process_routing(
            ctx=ctx,
            container=container,
            payload=payload,
            module_key=get_module_for_intent(payload.intent),
            handle_method="handle_intent",
            log_label="INTENT"
        )
            
    async def _handle_unknown_type(
        self,
        ctx: "ActivityContextWrapper",
        payload: Union[ActionPayload, IntentPayload],
        container: "ServiceContainer"
    ) -> None:
        """
        Handle unknown request types.
        """
        await self._report_routing_error(
            ctx, 
            f"Unknown request type encountered during dispatch."
        )
    
    async def _process_routing(
        self,
        ctx: "ActivityContextWrapper",
        container: "ServiceContainer",
        payload: Union[ActionPayload, IntentPayload],
        module_key: Optional[BotModule],
        handle_method: str,
        log_label: str
    ) -> None:
        """
        Centralized processing logic for routing to controllers.
        """
        
        controller = await self.resolve_controller(
            container,
            module_key,
            log_label
        )
        if not controller:
            return await self._report_routing_error(
                ctx, 
                f"CRITICAL: No controller resolved for module {module_key} during {log_label} routing."
            )

        try:
            handle_func = getattr(controller, handle_method)
            logger.info(f"{log_label} routed to {controller.__class__.__name__} for module {module_key}")
            await handle_func(ctx, payload)
        except Exception as e:
            logger.error(f"Error while handling {log_label} in {controller.__class__.__name__}: {e}", exc_info=True)
            await self._report_routing_error(
                ctx, 
                f"Error processing your request. Please try again later."
            )
    
    async def resolve_controller(
        self,
        container: "ServiceContainer",
        module_key: BotModule,
        log_label: str
    ) -> Optional[BaseController]:
        """
        Resolve and return the controller for a given module key.
        """
        if not module_key:
            logger.error(f"CRITICAL: {log_label} is not mapped to any module in registry.py")
            return
        
        feature = container.features.get(module_key)
        if not feature:
            logger.error(f"CRITICAL: No controller found for module {module_key} during resolution.")
            return None
        return feature.controller
    
    async def _report_routing_error(
        self, 
        ctx: "ActivityContextWrapper", 
        log_message: str
        ) -> None:
        """
        Centralized error handling for non-routable requests.
        Logs the warning and sends a localized user-friendly message.
        """
        logger.warning(log_message)
        language = get_user_language(ctx)
        message = get_translation(TranslationKey.MESSAGE_UNHANDLED_REQUEST, language)
        await ctx.send_activity(message)


__all__ = (
    "BotDispatcher",
)

