import logging
from typing import TYPE_CHECKING, Optional, Any

from core.enums.bot import (
    BotModule,
    BotRequestType,
    get_module_for_action,
    get_module_for_intent
)
from core.enums.translation_key import TranslationKey
from core.utils.helpers import get_user_language

from schemas.bot import ActionPayload, IntentPayload

from resources import get_translation


if TYPE_CHECKING:
    from bot.activity_context_wrapper import ActivityContextWrapper
    from core.containers.service_container import ServiceContainer
    

logger = logging.getLogger(__name__)


class BotDispatcher:
    
    async def dispatch(
        self,
        ctx: "ActivityContextWrapper",
        request: "ClassifiedRequest",
        container: "ServiceContainer"
    ) -> None:
        """
        Level 1 dispatcher: Routes messages to module controllers.
        """
        if request.request_type == BotRequestType.ACTION:
            await self._dispatch_action(ctx, request.payload, container)
        elif request.request_type == BotRequestType.INTENT:
            await self._dispatch_intent(ctx, request.payload, container)
        else:
            await self._handle_non_routable_request(
                ctx, 
                f"Unknown request type: {request.request_type}"
                )
            
    async def _dispatch_action(
        self,
        ctx: "ActivityContextWrapper",
        payload: ActionPayload,
        container: "ServiceContainer"
    ) -> None:
        """
        Level 1: Routes action (button click) to appropriate module controller.
        """
        module_key = get_module_for_action(payload.action)
        if not module_key:
            await self._handle_non_routable_request(
                ctx, 
                f"Unknown action '{payload.action}' - no module found in registry"
            )
            return

        controller = await self._resolve_controller(
            container,
            module_key
        )
        if controller:
            logger.info(f"Routing ACTION '{payload.action}' to module '{module_key.value}'")
            await controller.handle_action(ctx, payload, container)
            
    async def _dispatch_intent(
        self,
        ctx: "ActivityContextWrapper",
        payload: IntentPayload,
        container: "ServiceContainer"
    ) -> None:
        """
        Level 1: Routes AI intent to appropriate module controller.
        """
        module_key = get_module_for_intent(payload.intent)
        if not module_key:
            await self._handle_non_routable_request(
                ctx, 
                f"Unknown intent '{payload.intent}' - no module found in registry"
            )
            return

        controller = await self._resolve_controller(
            container,
            module_key
        )
        if controller:
            logger.info(f"Routing INTENT '{payload.intent}' to module '{module_key.value}'")
            await controller.handle_intent(ctx, payload, container)
    
    # TODO: Return type hint for ClassifiedRequest
    def _resolve_controller(
        self, 
        container: "ServiceContainer",
        module_key: BotModule
        ) -> Optional[Any]:
        """
        Attempts to find a controller for the module. 
        If missing, handles the error communication automatically.
        """
        controller = container.features.get(module_key)
        if not controller:
            logger.error(f"No controller found for module: {module_key}")
        return controller
    
    async def _handle_non_routable_request(
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




























# import logging
# from typing import TYPE_CHECKING, Optional

# from enums.bot import BotModule, get_module_for_action
# from enums.translation_key import TranslationKey
# from handlers.registry import get_controller
# from models.action import ActionPayload
# from utils.helpers import get_user_language
# from resources import get_translation
# from schemas.ai import UserIntent

# if TYPE_CHECKING:
#     from bot.activity_context_wrapper import ActivityContextWrapper
#     from core.containers.service_container import ServiceContainer
#     from handlers.registry import ModuleController

# logger = logging.getLogger("HRBot")


# class BotDispatcher:
#     """
#     Level 1 dispatcher: Routes messages to module controllers.
#     """

#     async def dispatch_action(
#         self,
#         ctx: "ActivityContextWrapper",
#         payload: ActionPayload,
#         container: "ServiceContainer"
#     ) -> None:
#         """
#         Level 1: Routes action (button click) to appropriate module controller.
#         """
#         module = get_module_for_action(payload.action)
#         if not module:
#             await self._handle_unrouted_request(
#                 ctx, 
#                 f"⚠️ Unknown action '{payload.action}' - no module found in registry"
#             )
#             return

#         controller = await self._resolve_controller(
#             ctx,
#             module,
#             context_info=f"action: '{payload.action}'"
#         )
#         logger.info(f"🔄 Level 1: Routing ACTION '{payload.action}' to module '{module.value}'")
#         await controller.handle_action(ctx, payload, container)

#     async def dispatch_intent(
#         self,
#         ctx: "ActivityContextWrapper",
#         user_intent: UserIntent,
#         container: "ServiceContainer"
#     ) -> None:
#         """
#         Level 1: Routes AI intent to appropriate module controller.
#         """
#         controller = await self._resolve_controller(
#             ctx,
#             user_intent.module,
#             context_info=f"intent: '{user_intent.intent}'"
#         )
#         logger.info(f"🔄 Level 1: Routing INTENT '{user_intent.intent}' to module '{user_intent.module}'")
#         await controller.handle_intent(ctx, user_intent, container)

#     # =========================================================================
#     # PRIVATE HELPERS
#     # =========================================================================

#     async def _handle_unrouted_request(self, ctx: "ActivityContextWrapper", log_message: str) -> None:
#         """
#         Centralized error handling for unroutable requests.
#         Logs the warning and sends a localized user-friendly message.
#         """
#         logger.warning(log_message)
        
#         language = get_user_language(ctx)
#         message = get_translation(TranslationKey.MESSAGE_UNHANDLED_REQUEST, language)
        
#         await ctx.send_activity(message)
        
#     async def _resolve_controller(
#         self, 
#         ctx: "ActivityContextWrapper",
#         module: BotModule,
#         context_info: str = ""
#         ) -> Optional["ModuleController"]:
#         """
#         Attempts to find a controller for the module. 
#         If missing, handles the error communication automatically.
#         """
#         controller = get_controller(module)
#         if not controller:
#             logger.error(f"❌ No controller found for module: {module}")
#             await self._handle_unrouted_request(
#                 ctx,
#                 f"❌ No controller found for module: {module}. ({context_info})"
#             )
#             return None
#         return controller