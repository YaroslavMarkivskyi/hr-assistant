"""
Bot Dispatcher - Level 1: Module-level routing

This is the "traffic controller" at the intersection.
It doesn't look at details (intent="book_meeting"), only at direction (module="scheduling").

Two-Level Architecture:
- Level 1 (this file): Routes by module
- Level 2 (module controllers): Routes by intent/action within module
"""
import logging
from typing import TYPE_CHECKING

from enums.bot import BotModule, get_module_for_action, get_module_for_intent
from enums.translation_key import TranslationKey
from handlers.registry import get_controller, GENERAL_MODULE
from models.action import ActionPayload
from models.ai import AIResponse
from utils.helpers import get_user_language
from resources import get_translation
from schemas.ai import UserIntent


if TYPE_CHECKING:
    from bot.activity_context_wrapper import ActivityContextWrapper
    from container import ServiceContainer

logger = logging.getLogger("HRBot")


class BotDispatcher:
    """
    Level 1 dispatcher: Routes messages to module controllers.
    
    This dispatcher trusts AI's decision about the module and delegates
    to the appropriate module controller. It doesn't know about specific
    intents or actions - that's the controller's responsibility.
    """    
    @staticmethod
    def _get_module_name(module: BotModule | None) -> str:
        """
        Get human-readable module name.
        
        Args:
            module: BotModule or GENERAL_MODULE (None)
            
        Returns:
            Module name string ("scheduling", "General", etc.)
        """
        if module is GENERAL_MODULE:
            return "General"
        return module.value if module else "General"

    async def dispatch_action(
        self,
        ctx: "ActivityContextWrapper",
        payload: ActionPayload,
        container: "ServiceContainer"
    ) -> None:
        """
        Level 1: Routes action to appropriate module controller.
        
        Args:
            ctx: Activity context from Teams
            payload: Validated ActionPayload from the card
            container: Service container with all services
        """
        action_enum = payload.action
        # Use registry to find which module owns this action
        module = get_module_for_action(action_enum.value)

        if not module:
            logger.warning(f"⚠️ Unknown action '{action_enum.value}' - no module found in registry")
            language = get_user_language(ctx)
            await ctx.send_activity(
                get_translation(TranslationKey.MESSAGE_UNHANDLED_REQUEST, language)
            )
            return

        # Level 2: Get module controller and delegate
        controller = get_controller(module)
        if not controller:
            logger.warning(
                f"⚠️ No controller registered for module '{module.value}' "
                f"(action: '{action_enum.value}')"
            )
            language = get_user_language(ctx)
            await ctx.send_activity(
                get_translation(TranslationKey.MESSAGE_UNHANDLED_REQUEST, language)
            )
            return

        logger.info(f"🔄 Level 1: Routing ACTION '{action_enum.value}' to module '{module.value}'")
        await controller.handle_action(ctx, payload, container)

    async def dispatch_intent(
        self,
        ctx: "ActivityContextWrapper",
        user_intent: UserIntent,
        container: "ServiceContainer"
    ) -> None:
        """
        Level 1: Routes intent to appropriate module controller.
        
        Trusts AI's decision about the module from ai_response.module.
        If module is None (general intents), routes to GeneralController.
        
        Args:
            ctx: Activity context wrapper
            intent: Intent string (e.g., "onboarding", "schedule_meeting")
            ai_response: Validated AIResponse model with full structured data
            container: Service container with all services
        """
        
        controller = get_controller(user_intent.module)
        
        logger.info(f"🤖 Dispatching intent '{user_intent.intent}' to module '{user_intent.module}'")
            
        if not controller:
            logger.warning(
                f"⚠️ CRITICAL: Module '{user_intent.module}' is defined in Enums "
                f"but has NO REGISTERED CONTROLLER! Intent: '{user_intent.intent}'"
            )
            language = get_user_language(ctx)
            await ctx.send_activity(
                get_translation(TranslationKey.MESSAGE_UNHANDLED_REQUEST, language)
            )
            return

        logger.info(f"🔄 Level 1: Routing INTENT '{user_intent.intent}' to module '{user_intent.module}'")
        await controller.handle_intent(ctx, user_intent, container)

