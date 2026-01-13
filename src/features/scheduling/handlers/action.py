import logging

from typing import Dict, Any, Callable
from datetime import datetime

from enums.bot import SchedulingAction, BotAction
from features.scheduling.service import SchedulingService
from ..models import ActionContext, BookSlotContext, BookingConfirmationViewModel
from ..views import create_booking_confirmation_card


logger = logging.getLogger("HRBot")


class SchedulingActionHandler:
    """
    Handler for scheduling-related actions.
    """
    def __init__(self, service: SchedulingService) -> None:
        self._service = service
        self._action_map: Dict[BotAction, Callable[[ActionContext], Any]] = {
            SchedulingAction.SHOW_MORE_SLOTS: self._handle_show_more_slots_action,
            SchedulingAction.BOOK_SLOT: self._handle_book_slot_action,
        }
        
    async def handle(
        self,
        request: ActionContext,
    ) -> None:
        """
        Main entry point to handle scheduling actions.
        Routes to specific handler based on action type.
        """
        handler = self._action_map.get(request.payload.action)
        if not handler:
            logger.warning(f"⚠️ No handler for action: {request.payload.action}")
            await request.ctx.send_activity(
                f"⚠️ Unrecognized action: {request.payload.action}"
            )
            return
        await handler(request)
        
    # ========================================================================#
    # Action Handlers                                                         #
    # ========================================================================#
           
    async def _handle_show_more_slots_action(self, request: ActionContext) -> None:
        """
        Handles SHOW_MORE_SLOTS action.
        """
        await request.ctx.send_activity("Loading more time slots...")
    
    async def _handle_book_slot_action(self, request: ActionContext) -> None:
        """
        Handles BOOK_SLOT action.
        """
        logger.info(f"📅 Booking slot with data: {request.payload.context}")
        
        try:
            ctx = BookSlotContext.model_validate(request.payload.context or {})
        except Exception as e:
            logger.error(f"❌ Invalid booking context: {e}", exc_info=True)
            await request.ctx.send_activity("⚠️ Invalid booking data provided.")
            return
        
        await request.ctx.send_typing_activity()
        
        result = await self._service.book_meeting(
            requester_id=request.requester_id,
            subject=ctx.subject,
            participants=ctx.participants,
            start_time=ctx.start,  # ✅ start_time
            end_time=ctx.end,      # ✅ end_time
            agenda=ctx.agenda
        )
        
        if result.success:
            confirmation_card = create_booking_confirmation_card(
                BookingConfirmationViewModel(
                    subject=ctx.subject,
                    participants=ctx.participants,
                    duration=ctx.duration,
                    start_time_str=ctx.start.strftime("%Y-%m-%d %H:%M"),
                    agenda=ctx.agenda
                ),
            )
            
            await request.ctx.send_adaptive_card(confirmation_card)
        else:
            logger.error(f"❌ Booking failed: {result.error_message}")
            await request.ctx.send_activity(
                f"⚠️ Failed to book meeting: {result.error_message}"
            )


__all__ = [
    "SchedulingActionHandler",
]
