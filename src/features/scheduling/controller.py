from __future__ import annotations
import logging
from datetime import datetime, timedelta
from typing import List, TYPE_CHECKING

from core.base import BaseController
from core.enums.bot import BotModule

from handlers.registry import register_controller

from schemas.bot import ActionPayload, IntentPayload

from .views import (
    create_find_time_card,
    create_booking_confirmation_card,
    create_workshop_card,
    create_daily_briefing_card,
    create_schedule_card
)

from .schemas import Participant
from .mappers import SchedulingMapper


if TYPE_CHECKING:
    from core.containers.service_container import ServiceContainer
    from .service import SchedulingService
    from bot.activity_context_wrapper import ActivityContextWrapper



logger = logging.getLogger(__name__)


@register_controller(BotModule.SCHEDULING)
class SchedulingController(BaseController):
    def __init__(self, container: ServiceContainer, service: SchedulingService):
        super().__init__(container)
        
        self._service: SchedulingService = service
        
        
    async def handle_intent_find_time(
        self,
        ctx: ActivityContextWrapper,
        payload: IntentPayload,
    ) -> None:
        """Handle find_time intent"""
        requester_id = await self._get_requester_id_or_error(ctx)
        if not requester_id: return
        
        await ctx.send_typing_activity()
        
        map_request = await SchedulingMapper.map_to_find_time_request(
            requester_id=requester_id,
            payload=payload,
            container=self._container
        )
        result = await self._service.find_time(map_request)
        
        if not result.success:
            await ctx.send_activity(result.error or "Error finding time slots")
            return
        
        map_view = SchedulingMapper.map_to_find_time_view(result, map_request)
        card = create_find_time_card(map_view)
        await ctx.send_adaptive_card(card)


__all__ = (
    "SchedulingController",
)

