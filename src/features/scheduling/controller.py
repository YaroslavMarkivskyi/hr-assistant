"""
Scheduling Module Controller

Thin controller layer that orchestrates the flow:
- Receives intents/actions from dispatcher
- Calls SchedulingService for business logic
- Uses views.py to create Adaptive Cards
- Sends responses to user
"""
import logging
from typing import Dict, Any, Callable
from datetime import datetime, timedelta

from bot.activity_context_wrapper import ActivityContextWrapper
from enums.bot import SchedulingIntent, SchedulingAction, BotModule
from core.containers.service_container import ServiceContainer
from handlers.base import BaseModuleController
from handlers.registry import register_controller
from models.action import ActionPayload
from .views import (
    create_find_time_card,
    create_booking_confirmation_card,
    create_workshop_card,
    create_daily_briefing_card,
    create_schedule_card,
)
from .models import TimeSlot, Participant, IntentContext, ActionContext
from .mappers import SchedulingMapper
from .service import SchedulingService
from schemas.ai import UserIntent

from .handlers import SchedulingActionHandler


logger = logging.getLogger("HRBot")


@register_controller(BotModule.SCHEDULING)
class SchedulingController(BaseModuleController):
    """
    Controller for Scheduling module.
    Orchestrates flow between Dispatcher -> Service -> Views.
    """ 
    def __init__(self, service: SchedulingService):
        super().__init__(service)
        
        # 1. Intent Map (Text -> Logic)
        self._intent_handlers: Dict[SchedulingIntent, Callable[[IntentContext], Any]] = {
            SchedulingIntent.FIND_TIME: self._handle_find_time_intent,
            SchedulingIntent.BOOK_MEETING: self._handle_book_meeting_intent,
            SchedulingIntent.UPDATE_MEETING: self._handle_update_meeting_intent,
            SchedulingIntent.CANCEL_MEETING: self._handle_cancel_meeting_intent,
            SchedulingIntent.CREATE_WORKSHOP: self._handle_create_workshop_intent,
            SchedulingIntent.DAILY_BRIEFING: self._handle_daily_briefing_intent,
            SchedulingIntent.VIEW_SCHEDULE: self._handle_view_schedule_intent,
        }
        
        self._action_handler = SchedulingActionHandler(service)
    
    # =========================================================================
    # DISPATCHERS (Entry Points)
    # =========================================================================
    
    async def handle_intent(
        self,
        ctx: ActivityContextWrapper,
        user_intent: UserIntent,
        container: ServiceContainer
    ) -> None:
        """Handles text commands via AI."""
        requester_id = await self._get_requester_id_or_error(ctx, container)
        if not requester_id: return
                
        handler = self._intent_handlers.get(user_intent.intent)
        if handler:
            context = IntentContext(
                requester_id=requester_id,
                ctx=ctx,
                container=container,
                user_intent=user_intent
            )
            try:
                await handler(context)
            except Exception as e:
                logger.error(f"❌ Error handling intent {user_intent.intent}: {e}", exc_info=True)
                await ctx.send_activity(f"Error processing request: {str(e)}")
        else:
            logger.warning(f"⚠️ Unhandled Scheduling intent: {user_intent.intent}")
            await self._send_unhandled_request(ctx)
        
    async def handle_action(
        self,
        ctx: ActivityContextWrapper,
        payload: ActionPayload,
        container: ServiceContainer
    ) -> None:
        """Routes action (button click) to appropriate handler."""
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
            logger.error(f"❌ Error handling action {payload.action}: {e}", exc_info=True)
            await ctx.send_activity(f"Error processing action: {str(e)}")
            logger.warning(f"⚠️ Unhandled Scheduling action: {payload.action}")
            await self._send_unhandled_request(ctx)
    
    # =========================================================================
    # INTENT HANDLERS (Text)
    # =========================================================================
    
    async def _handle_find_time_intent(self, request: IntentContext) -> None:
        """Handle find_time intent"""
        await request.ctx.send_typing_activity()
        
        map_request = await SchedulingMapper.map_to_find_time_request(request)
        result = await self._service.find_time(map_request)
        
        if not result.success:
            await request.ctx.send_activity(result.error or "Error finding time slots")
            return
        
        map_view = SchedulingMapper.map_to_find_time_view(result, map_request)
        card = create_find_time_card(map_view)
        await request.ctx.send_adaptive_card(card)
    
    async def _handle_book_meeting_intent(self, request: IntentContext) -> None:
        """Handle book_meeting intent"""
        entities = request.user_intent.entities
        
        # Extract entities
        participants_data = entities.get("participants", [])
        subject = entities.get("subject", "Зустріч")
        duration = entities.get("duration", 30)
        agenda = entities.get("agenda")
        
        # Convert participants
        participants = [
            Participant(**p) if isinstance(p, dict) else p
            for p in participants_data
        ]
        
        # Calculate time (Simple fallback logic for now)
        start_time = datetime.utcnow() + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=duration)
        
        # Call Service
        result = await self._service.book_meeting(
            requester_id=request.requester_id,
            subject=subject,
            participants=participants,
            start_time=start_time,
            end_time=end_time,
            agenda=agenda
        )
        
        if not result.success:
            await request.ctx.send_activity(result.error or "Помилка бронювання зустрічі")
            return
        
        # Create View
        result_participants = result.resolved_participants or participants
        card = create_booking_confirmation_card(
            subject=subject,
            participants=result_participants,
            start_time=result.data.get("start_time"),
            end_time=result.data.get("end_time"),
            duration=duration,
            agenda=agenda
        )
        await request.ctx.send_adaptive_card(card)

    async def _handle_update_meeting_intent(self, request: IntentContext) -> None:
        """Handle update_meeting intent"""
        entities = request.user_intent.entities
        meeting_id = entities.get("meeting_id")
        
        if not meeting_id:
            await request.ctx.send_activity("Не вказано ID зустрічі для оновлення")
            return
        
        result = await self._service.update_meeting(
            requester_id=request.requester_id,
            meeting_id=meeting_id,
            start_time=None, 
            end_time=None,
            subject=entities.get("subject"),
            participants=entities.get("participants")
        )
        
        if not result.success:
            await request.ctx.send_activity(result.error or "Помилка оновлення зустрічі")
        else:
            await request.ctx.send_activity("Зустріч успішно оновлено")

    async def _handle_cancel_meeting_intent(self, request: IntentContext) -> None:
        """Handle cancel_meeting intent"""
        entities = request.user_intent.entities
        meeting_id = entities.get("meeting_id")
        
        if not meeting_id:
            await request.ctx.send_activity("Не вказано ID зустрічі для скасування")
            return
        
        result = await self._service.cancel_meeting(
            requester_id=request.requester_id,
            meeting_id=meeting_id
        )
        
        if not result.success:
            await request.ctx.send_activity(result.error or "Помилка скасування зустрічі")
        else:
            await request.ctx.send_activity("Зустріч успішно скасовано")

    async def _handle_create_workshop_intent(self, request: IntentContext) -> None:
        """Handle create_workshop intent"""
        card = create_workshop_card()
        await request.ctx.send_adaptive_card(card)

    async def _handle_daily_briefing_intent(self, request: IntentContext) -> None:
        """Handle daily_briefing intent"""
        entities = request.user_intent.entities
        date = entities.get("date") or entities.get("preferredDate")
        
        result = await self._service.daily_briefing(
            requester_id=request.requester_id,
            date=date
        )
        
        if not result.success:
            await request.ctx.send_activity(result.error or "Помилка отримання календаря")
            return
        
        events = result.data.get("events", [])
        now = datetime.utcnow()
        card = create_daily_briefing_card(events, now)
        await request.ctx.send_adaptive_card(card)

    async def _handle_view_schedule_intent(self, request: IntentContext) -> None:
        """Handle view_schedule intent"""
        entities = request.user_intent.entities
        employee_id = entities.get("employee_id")
        employee_name = entities.get("employee_name")
        date = entities.get("date") or entities.get("preferredDate")
        detailed = entities.get("detailed", True)
        
        result = await self._service.view_schedule(
            requester_id=request.requester_id,
            employee_id=employee_id,
            employee_name=employee_name,
            date=date,
            detailed=detailed
        )
        
        if not result.success:
            await request.ctx.send_activity(result.error or "Помилка перегляду розкладу")
            return
        
        # Prepare View
        timeline_slots = result.data.get("timeline_slots", [])
        resolved_employee_name = result.data.get("employee_name") or employee_name or "Користувач"
        date_str = result.data.get("date", datetime.utcnow().isoformat())
        
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            date_display = date_obj.strftime("%d.%m.%Y")
        except (ValueError, AttributeError):
            date_display = date_str
        
        card = create_schedule_card(
            employee_name=resolved_employee_name,
            date_str=date_display,
            grouped_slots=timeline_slots
        )
        await request.ctx.send_adaptive_card(card)

    # =========================================================================
    # ACTION HANDLERS (Buttons)
    # =========================================================================
    
    async def _handle_find_time_action(self, request: ActionContext) -> None:
        """Handle actions related to finding time slots"""
        action = request.payload.action
        data = request.payload.context or {}

        if action == SchedulingAction.BOOK_SLOT:
            # ✅ Реалізація логіки кнопки "Забронювати"
            await request.ctx.send_typing_activity()
            
            start_str = data.get("start")
            end_str = data.get("end")
            subject = data.get("subject", "Meeting")
            
            if not start_str or not end_str:
                await request.ctx.send_activity("❌ Помилка: Некоректні дані слота.")
                return

            try:
                start_time = datetime.fromisoformat(start_str)
                end_time = datetime.fromisoformat(end_str)
            except ValueError:
                await request.ctx.send_activity("❌ Помилка: Невірний формат дати.")
                return

            # Викликаємо сервіс (тут поки заглушка, або ваш мок)
            # Примітка: request.container.scheduling_service доступний через геттер self._service
            result = await self._service.book_meeting(
                requester_id=request.requester_id,
                subject=subject,
                participants=[], # TODO: Дістати учасників із контексту, якщо ми їх туди передавали
                start_time=start_time,
                end_time=end_time
            )

            if result.success:
                # Відправляємо картку підтвердження
                card = create_booking_confirmation_card(
                    subject=subject,
                    participants=[],
                    start_time=start_time,
                    end_time=end_time,
                    duration=int((end_time - start_time).total_seconds() / 60)
                )
                await request.ctx.send_adaptive_card(card)
            else:
                await request.ctx.send_activity(f"❌ Не вдалося забронювати: {result.error}")

        elif action == SchedulingAction.SHOW_MORE_SLOTS:
            await request.ctx.send_activity("Функціонал 'Більше варіантів' в розробці 🚧")
        
        else:
            await request.ctx.send_activity(f"Дія {action} ще не реалізована.")
    
    async def _handle_booking_action(self, request: ActionContext) -> None:
        """Handle booking details actions"""
        await request.ctx.send_activity("Дія бронювання в розробці")
    
    async def _handle_crud_action(self, request: ActionContext) -> None:
        """Handle CRUD actions"""
        await request.ctx.send_activity("Дія редагування в розробці")
    
    async def _handle_workshop_action(self, request: ActionContext) -> None:
        """Handle Workshop actions"""
        await request.ctx.send_activity("Дія воркшопу в розробці")
    
    async def _handle_daily_briefing_action(self, request: ActionContext) -> None:
        """Handle Briefing details"""
        await request.ctx.send_activity("Дія бриффінгу в розробці")