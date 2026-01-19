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
    from .services import SchedulingService
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
        requester_id = await self._get_requester_id_or_error(ctx, self._container)
        if not requester_id: return
        
        map_request = await SchedulingMapper.map_to_find_time_request(
            requester_id=requester_id,
            payload=payload
        )
        result = await self._service.find_time(map_request)
        
        if not result.success:
            await ctx.send_activity(result.error or "Error finding time slots")
            return
        
        map_view = SchedulingMapper.map_to_find_time_view(result, map_request)
        card = create_find_time_card(map_view)
        await ctx.send_adaptive_card(card)


# """
# Scheduling Module Controller

# Orchestrates the flow for scheduling operations using dynamic routing.
# Dispatcher -> Controller -> Service -> Views.
# """
# import logging
# from datetime import datetime, timedelta
# from typing import List

# from bot.activity_context_wrapper import ActivityContextWrapper
# from core.base import BaseController
# from core.enums.bot import BotModule
# from handlers.registry import register_controller
# from schemas.bot import ActionPayload, IntentPayload

# from .views import (
#     create_find_time_card,
#     create_booking_confirmation_card,
#     create_workshop_card,
#     create_daily_briefing_card,
#     create_schedule_card,
# )
# from .schemas import Participant
# from .mappers import SchedulingMapper
# from .service import SchedulingService

# logger = logging.getLogger("HRBot")


# @register_controller(BotModule.SCHEDULING)
# class SchedulingController(BaseController):
#     """
#     Controller for Scheduling module.
#     Inherits dynamic routing and localization helpers from BaseController.
#     """
#     def __init__(self, container: "ServiceContainer"):
#         super().__init__(container)
#         # Отримуємо сервіс із контейнера. 
#         # Переконайтеся, що у вашому FeatureRegistry є такий метод або доступ.
#         self._service: SchedulingService = container.features.get(BotModule.SCHEDULING).service

#     # =========================================================================
#     # INTENT HANDLERS (handle_intent_{intent_name})
#     # =========================================================================

#     async def handle_intent_find_time(self, ctx: ActivityContextWrapper, payload: IntentPayload) -> None:
#         """Обробка наміру пошуку вільного часу."""
#         requester_id = await self._get_requester_id_or_error(ctx)
#         if not requester_id: return

#         await ctx.send_typing_activity()
        
#         # Мапимо дані напряму з payload
#         map_request = await SchedulingMapper.map_payload_to_find_time_request(requester_id, payload)
#         result = await self._service.find_time(map_request)
        
#         if not result.success:
#             await ctx.send_activity(result.error or "Error finding time slots")
#             return
        
#         map_view = SchedulingMapper.map_to_find_time_view(result, map_request)
#         card = create_find_time_card(map_view)
#         await ctx.send_adaptive_card(card)

#     async def handle_intent_book_meeting(self, ctx: ActivityContextWrapper, payload: IntentPayload) -> None:
#         """Бронювання зустрічі через текст."""
#         requester_id = await self._get_requester_id_or_error(ctx)
#         if not requester_id: return

#         entities = payload.entities
#         participants_data = entities.get("participants", [])
#         subject = entities.get("subject", "Зустріч")
#         duration = entities.get("duration", 30)
        
#         participants = [Participant(**p) if isinstance(p, dict) else p for p in participants_data]
        
#         # Спрощена логіка часу (на 1 годину вперед)
#         start_time = datetime.utcnow() + timedelta(hours=1)
#         end_time = start_time + timedelta(minutes=duration)
        
#         result = await self._service.book_meeting(
#             requester_id=requester_id,
#             subject=subject,
#             participants=participants,
#             start_time=start_time,
#             end_time=end_time,
#             agenda=entities.get("agenda")
#         )
        
#         if not result.success:
#             await ctx.send_activity(result.error or "Помилка бронювання")
#             return
        
#         card = create_booking_confirmation_card(
#             subject=subject,
#             participants=result.resolved_participants or participants,
#             start_time=result.data.get("start_time"),
#             end_time=result.data.get("end_time"),
#             duration=duration
#         )
#         await ctx.send_adaptive_card(card)

#     async def handle_intent_cancel_meeting(self, ctx: ActivityContextWrapper, payload: IntentPayload) -> None:
#         """Скасування зустрічі."""
#         requester_id = await self._get_requester_id_or_error(ctx)
#         if not requester_id: return

#         meeting_id = payload.entities.get("meeting_id")
#         if not meeting_id:
#             await ctx.send_activity("Будь ласка, вкажіть ID зустрічі.")
#             return

#         result = await self._service.cancel_meeting(requester_id, meeting_id)
#         message = "Зустріч успішно скасовано" if result.success else (result.error or "Помилка скасування")
#         await ctx.send_activity(message)

#     async def handle_intent_daily_briefing(self, ctx: ActivityContextWrapper, payload: IntentPayload) -> None:
#         """Резюме дня."""
#         requester_id = await self._get_requester_id_or_error(ctx)
#         if not requester_id: return

#         date = payload.entities.get("date") or payload.entities.get("preferredDate")
#         result = await self._service.daily_briefing(requester_id, date)
        
#         if result.success:
#             card = create_daily_briefing_card(result.data.get("events", []), datetime.utcnow())
#             await ctx.send_adaptive_card(card)
#         else:
#             await ctx.send_activity("Не вдалося отримати розклад.")

#     # =========================================================================
#     # ACTION HANDLERS (handle_action_{action_name})
#     # =========================================================================

#     async def handle_action_book_slot(self, ctx: ActivityContextWrapper, payload: ActionPayload) -> None:
#         """Кнопка 'Забронювати' з Adaptive Card."""
#         requester_id = await self._get_requester_id_or_error(ctx)
#         if not requester_id: return

#         data = payload.data or {}
#         try:
#             start_time = datetime.fromisoformat(data.get("start"))
#             end_time = datetime.fromisoformat(data.get("end"))
#             subject = data.get("subject", "Meeting")
            
#             result = await self._service.book_meeting(
#                 requester_id=requester_id,
#                 subject=subject,
#                 participants=[],
#                 start_time=start_time,
#                 end_time=end_time
#             )

#             if result.success:
#                 card = create_booking_confirmation_card(
#                     subject=subject,
#                     participants=[],
#                     start_time=start_time,
#                     end_time=end_time,
#                     duration=int((end_time - start_time).total_seconds() / 60)
#                 )
#                 await ctx.send_adaptive_card(card)
#             else:
#                 await ctx.send_activity(f"❌ Помилка: {result.error}")
#         except Exception as e:
#             logger.error(f"Error booking slot via action: {e}")
#             await ctx.send_activity("❌ Некоректні дані слота.")

#     async def handle_action_show_more_slots(self, ctx: ActivityContextWrapper, payload: ActionPayload) -> None:
#         """Кнопка 'Показати більше'."""
#         await ctx.send_activity("Шукаю додаткові варіанти... 🚧")

# __all__ = ("SchedulingController",)