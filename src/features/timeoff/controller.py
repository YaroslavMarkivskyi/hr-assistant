import logging
from typing import Dict, Callable, Any

from bot.activity_context_wrapper import ActivityContextWrapper
from enums.bot import BotModule
from core.containers.service_container import ServiceContainer

from handlers.base import BaseModuleController
from handlers.registry import register_controller

from models.action import ActionPayload
from schemas.ai import UserIntent

from enums.bot.intents import TimeOffIntent
from features.scheduling.models import IntentContext, ActionContext
from .service import TimeOffService
from .handlers import TimeOffIntentHandler, TimeOffActionHandler


logger = logging.getLogger("TimeOffController")


@register_controller(BotModule.TIME_OFF)
class TimeOffController(BaseModuleController):
    """
    Controller for Time Off module.
    Orchestrates flow between Dispatcher -> Handlers -> Service -> Views.
    """
    
    def __init__(self, service: TimeOffService):
        super().__init__(service)
        
        # TODO add service 
        self._intent_handler = TimeOffIntentHandler(service)
        self._action_handler = TimeOffActionHandler(service)
        
    async def handle_intent(
        self,
        ctx: ActivityContextWrapper,
        user_intent: UserIntent,
        container: ServiceContainer
    ) -> None:
        """
        Routes text commands to IntentHandler.
        """
        logger.info(f"⏳ Handling TimeOff intent: {user_intent.intent}")
        
        requester_id = await self._get_requester_id_or_error(ctx, container)
        if not requester_id: return
        
        context = IntentContext(
            requester_id=requester_id,
            ctx=ctx,
            container=container,
            user_intent=user_intent
        )
        try:
            await self._intent_handler.handle(context)
        except Exception as e:
            logger.error(f"❌ Error handling TimeOff intent: {e}", exc_info=True)
            await ctx.send_activity("❌ An error occurred while processing your request.")
            
    async def handle_action(
        self,
        ctx: ActivityContextWrapper,
        payload: ActionPayload,
        container: ServiceContainer
    ) -> None:
        """
        Routes action commands to ActionHandler.
        """
        logger.info(f"⏳ Handling TimeOff action: {payload.action}")
        
        requester_id = await self._get_requester_id_or_error(ctx, container)
        if not requester_id: return
        
        context = ActionContext(
            requester_id=requester_id,
            ctx=ctx,
            container=container,
            payload=payload
        )
        try:
            await self._action_handler.handle(context)
        except Exception as e:
            logger.error(f"❌ Error handling TimeOff action {payload.action}: {e}", exc_info=True)
            await ctx.send_activity("❌ An error occurred while processing your action.")
        

