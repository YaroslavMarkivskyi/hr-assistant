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
from enums.bot import SchedulingIntent, BotAction, BotModule
from container import ServiceContainer
from enums.translation_key import TranslationKey
from handlers.base import BaseModuleController
from handlers.registry import register_controller
from models.action import ActionPayload
from models.ai import AIResponse
from .views import (
    create_find_time_card,
    create_booking_confirmation_card,
    create_workshop_card,
    create_daily_briefing_card,
    create_schedule_card,
)
from .models import TimeSlot, Participant, IntentContext
from .mappers import SchedulingMapper
from .service import SchedulingService
from schemas.ai import UserIntent

logger = logging.getLogger("HRBot")


@register_controller(BotModule.SCHEDULING)
class SchedulingController(BaseModuleController):
    """
    Controller for Scheduling module.
    
    Thin controller that:
    - Routes intents/actions to service methods
    - Handles service responses
    - Creates UI (Adaptive Cards) via views
    - Sends responses to user
    """ 
    def __init__(self, service: SchedulingService):
        super().__init__(service)
        self._intent_handlers: Dict[SchedulingIntent, Callable] = {
            SchedulingIntent.FIND_TIME: self._handle_find_time_intent,
            SchedulingIntent.BOOK_MEETING: self._handle_book_meeting_intent,
            SchedulingIntent.UPDATE_MEETING: self._handle_update_meeting_intent,
            SchedulingIntent.CANCEL_MEETING: self._handle_cancel_meeting_intent,
            SchedulingIntent.CREATE_WORKSHOP: self._handle_create_workshop_intent,
            SchedulingIntent.DAILY_BRIEFING: self._handle_daily_briefing_intent,
            SchedulingIntent.VIEW_SCHEDULE: self._handle_view_schedule_intent,
        }
        
        # TODO: Action map can be added similarly if needed
    
    
    async def handle_intent(
        self,
        ctx: ActivityContextWrapper,
        user_intent: UserIntent,
        container: ServiceContainer
    ) -> None:
        """
        Handles Scheduling module intents (text messages).
        
        Args:
            ctx: Activity context wrapper
            intent: Intent string (e.g., "find_time", "book_meeting")
            ai_response: Validated AIResponse from AI service
            container: Service container with all services
        """
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
        """
        Handles Scheduling module actions (button clicks from Adaptive Cards).
        
        Args:
            ctx: Activity context
            payload: Validated ActionPayload from the card
            container: Service container with all services
        """
        action_enum = payload.action
        requester_id = await self._get_requester_id_or_error(ctx, container)
        
        if not requester_id:
            return
        
        # Extract context from payload
        context = payload.context or {}
        
        service = container.scheduling_service
        
        try:
            # Route actions to appropriate handlers
            if action_enum in [BotAction.SELECT_TIME_SLOT, BotAction.SHOW_MORE_SLOTS, BotAction.BOOK_SLOT]:
                await self._handle_find_time_action(ctx, service, requester_id, action_enum, context)
            elif action_enum in [BotAction.CONFIRM_BOOKING, BotAction.ADD_EXTERNAL_GUEST, BotAction.ADD_GROUP]:
                await self._handle_booking_action(ctx, service, requester_id, action_enum, context)
            elif action_enum in [BotAction.RESCHEDULE_MEETING, BotAction.CANCEL_MEETING, BotAction.UPDATE_NOTIFICATION_PREFERENCE]:
                await self._handle_crud_action(ctx, service, requester_id, action_enum, context)
            elif action_enum in [BotAction.IGNORE_AVAILABILITY_TOGGLE, BotAction.CONFIRM_WORKSHOP]:
                await self._handle_workshop_action(ctx, service, requester_id, action_enum, context)
            elif action_enum == BotAction.VIEW_CALENDAR_DETAILS:
                await self._handle_daily_briefing_action(ctx, service, requester_id, context)
            else:
                logger.warning(f"⚠️ Unhandled Scheduling action: {action_enum.value}")
                await self._send_unhandled_request(ctx)
        except Exception as e:
            logger.error(f"❌ Error handling action {action_enum.value}: {e}", exc_info=True)
            await ctx.send_activity(f"Виникла помилка при обробці дії: {str(e)}")
    
    # Intent handlers
    
    async def _handle_find_time_intent(
        self,
        request: IntentContext,
    ) -> None:
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
    
    async def _handle_book_meeting_intent(
        self,
        ctx: ActivityContextWrapper,
        service,
        requester_id: str,
        entities: Dict[str, Any]
    ) -> None:
        """Handle book_meeting intent"""
        # Extract entities
        participants_data = entities.get("participants", [])
        subject = entities.get("subject", "Зустріч")
        duration = entities.get("duration", 30)
        agenda = entities.get("agenda")
        
        # Convert participants from dict to Participant models
        participants = [
            Participant(**p) if isinstance(p, dict) else p
            for p in participants_data
        ]
        
        # Parse date/time
        # TODO: Parse preferredDate and preferredTime to datetime
        start_time = datetime.utcnow() + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=duration)
        
        # Call service
        result = await service.book_meeting(
            requester_id=requester_id,
            subject=subject,
            participants=participants,
            start_time=start_time,
            end_time=end_time,
            agenda=agenda
        )
        
        # Handle result
        if not result.success:
            await ctx.send_activity(result.error or "Помилка бронювання зустрічі")
            return
        
        # Extract participants from result (they're already Participant models)
        result_participants = result.resolved_participants or participants
        
        # Create confirmation card
        card = create_booking_confirmation_card(
            subject=subject,
            participants=result_participants,
            start_time=result.data.get("start_time"),
            end_time=result.data.get("end_time"),
            duration=duration,
            agenda=agenda
        )
        
        await ctx.send_adaptive_card(card)
    
    async def _handle_update_meeting_intent(
        self,
        ctx: ActivityContextWrapper,
        service,
        requester_id: str,
        entities: Dict[str, Any]
    ) -> None:
        """Handle update_meeting intent"""
        meeting_id = entities.get("meeting_id")
        if not meeting_id:
            await ctx.send_activity("Не вказано ID зустрічі для оновлення")
            return
        
        result = await service.update_meeting(
            requester_id=requester_id,
            meeting_id=meeting_id,
            start_time=None,  # TODO: Parse from entities
            end_time=None,
            subject=entities.get("subject"),
            participants=entities.get("participants")
        )
        
        if not result.success:
            await ctx.send_activity(result.error or "Помилка оновлення зустрічі")
        else:
            await ctx.send_activity("Зустріч успішно оновлено")
    
    async def _handle_cancel_meeting_intent(
        self,
        ctx: ActivityContextWrapper,
        service,
        requester_id: str,
        entities: Dict[str, Any]
    ) -> None:
        """Handle cancel_meeting intent"""
        meeting_id = entities.get("meeting_id")
        if not meeting_id:
            await ctx.send_activity("Не вказано ID зустрічі для скасування")
            return
        
        result = await service.cancel_meeting(
            requester_id=requester_id,
            meeting_id=meeting_id
        )
        
        if not result.success:
            await ctx.send_activity(result.error or "Помилка скасування зустрічі")
        else:
            await ctx.send_activity("Зустріч успішно скасовано")
    
    async def _handle_create_workshop_intent(
        self,
        ctx: ActivityContextWrapper,
        service,
        requester_id: str,
        entities: Dict[str, Any]
    ) -> None:
        """Handle create_workshop intent"""
        card = create_workshop_card()
        await ctx.send_adaptive_card(card)
    
    async def _handle_daily_briefing_intent(
        self,
        ctx: ActivityContextWrapper,
        service,
        requester_id: str,
        entities: Dict[str, Any]
    ) -> None:
        """Handle daily_briefing intent"""
        # Date can be string ("tomorrow", "2023-10-15") - service will parse it
        date = entities.get("date") or entities.get("preferredDate")
        
        result = await service.daily_briefing(
            requester_id=requester_id,
            date=date
        )
        
        if not result.success:
            await ctx.send_activity(result.error or "Помилка отримання календаря")
            return
        
        # Create briefing card
        events = result.data.get("events", [])
        now = datetime.utcnow()
        
        card = create_daily_briefing_card(events, now)
        await ctx.send_adaptive_card(card)
    
    async def _handle_view_schedule_intent(
        self,
        ctx: ActivityContextWrapper,
        service,
        requester_id: str,
        entities: Dict[str, Any]
    ) -> None:
        """Handle view_schedule intent"""
        # Extract employee info - can be ID or name
        employee_id = entities.get("employee_id")
        employee_name = entities.get("employee_name")
        # Date can be string ("tomorrow", "2023-10-15") or None - service will parse it
        date = entities.get("date") or entities.get("preferredDate")
        detailed = entities.get("detailed", True)  # Default to detailed view
        
        result = await service.view_schedule(
            requester_id=requester_id,
            employee_id=employee_id,
            employee_name=employee_name,
            date=date,
            detailed=detailed
        )
        
        if not result.success:
            await ctx.send_activity(result.error or "Помилка перегляду розкладу")
            return
        
        # Create schedule card
        timeline_slots = result.data.get("timeline_slots", [])
        # Use resolved employee name from service or fallback
        resolved_employee_name = result.data.get("employee_name") or employee_name or "Користувач"
        date_str = result.data.get("date", datetime.utcnow().isoformat())
        
        # Format date string for display
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
        
        await ctx.send_adaptive_card(card)
    
    # Action handlers
    
    async def _handle_find_time_action(
        self,
        ctx: ActivityContextWrapper,
        service,
        requester_id: str,
        action: BotAction,
        context: Dict[str, Any]
    ) -> None:
        """Handle find time related actions"""
        if action == BotAction.BOOK_SLOT:
            # Book the selected slot
            slot_data = context.get("slot_data", {})
            # TODO: Implement booking from slot
            await ctx.send_activity("Бронювання слота в розробці")
        else:
            await ctx.send_activity("Дія в розробці")
    
    async def _handle_booking_action(
        self,
        ctx: ActivityContextWrapper,
        service,
        requester_id: str,
        action: BotAction,
        context: Dict[str, Any]
    ) -> None:
        """Handle booking related actions"""
        if action == BotAction.CONFIRM_BOOKING:
            # TODO: Extract booking data from context and call service.book_meeting
            await ctx.send_activity("Підтвердження бронювання в розробці")
        else:
            await ctx.send_activity("Дія в розробці")
    
    async def _handle_crud_action(
        self,
        ctx: ActivityContextWrapper,
        service,
        requester_id: str,
        action: BotAction,
        context: Dict[str, Any]
    ) -> None:
        """Handle CRUD actions"""
        await ctx.send_activity("Дія в розробці")
    
    async def _handle_workshop_action(
        self,
        ctx: ActivityContextWrapper,
        service,
        requester_id: str,
        action: BotAction,
        context: Dict[str, Any]
    ) -> None:
        """Handle workshop related actions"""
        await ctx.send_activity("Дія в розробці")
    
    async def _handle_daily_briefing_action(
        self,
        ctx: ActivityContextWrapper,
        service,
        requester_id: str,
        context: Dict[str, Any]
    ) -> None:
        """Handle daily briefing actions"""
        await ctx.send_activity("Дія в розробці")
