from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from core.enums.prompts import PromptKeys # remove unused import

from features.scheduling.schemas import (
    FindTimeRequest, 
    ViewScheduleRequest, 
    CancelMeetingRequest, 
    DailyBriefingRequest,
    SchedulingResult,
    TimeSlot,
    FindTimeViewModel
)


if TYPE_CHECKING:
    from schemas.bot import IntentPayload
    from core.containers.service_container import ServiceContainer


logger = logging.getLogger(__name__)


class SchedulingMapper:
    @staticmethod
    async def map_to_find_time_request(
        requester_id: str,
        payload: IntentPayload,
        container: ServiceContainer
        ) -> FindTimeRequest:
        """Extracts meeting details using AI."""
        return FindTimeRequest(
            requester_id=requester_id,
            subject=payload.entities.get("subject") or "Meeting",
            participant_names=payload.entities.get("participants") or [],
            duration_minutes=payload.entities.get("duration_minutes") or 30,
            start_date=payload.entities.get("date"),
            time_preference=payload.entities.get("specific_time") or payload.entities.get("day_part")
        )

    @staticmethod
    async def map_to_view_schedule_request(
        requester_id: str,
        payload: IntentPayload,
        container: ServiceContainer
        ) -> ViewScheduleRequest:
        """Extracts target person and date."""
        entities = payload.entities
        target_person = entities.get("target_person")
        
        return ViewScheduleRequest(
            requester_id=requester_id,
            target_employee_name=target_person,
            target_employee_id=requester_id if not target_person else None, 
            date=entities.get("date"),
            detailed=True
        )

    # @staticmethod
    # async def map_to_cancel_request(ctx: IntentContext) -> CancelMeetingRequest:
    #     """Extracts keywords to identify meeting to cancel."""
    #     current_time = ctx.container.time_service.now()
    #     context_str = f"Current time: {current_time.strftime('%Y-%m-%d %H:%M')}"

    #     entities = await ctx.container.ai_service.extract_data(
    #         user_text=ctx.ctx.activity.text,
    #         result_type=ScheduleCancelEntities,
    #         prompt_key=PromptKeys.SCHEDULING_CANCEL,
    #         context=context_str
    #     )
        
    #     return CancelMeetingRequest(
    #         requester_id=ctx.requester_id,
    #         keywords=entities.subject_keywords,
    #         participants=entities.participants,
    #         target_date=entities.date
    #     )

    # @staticmethod
    # async def map_to_daily_briefing_request(ctx: IntentContext) -> DailyBriefingRequest:
    #     """
    #     Extracts date for briefing (e.g., 'briefing for tomorrow').
    #     Uses the same prompt as View Schedule because semantics are similar.
    #     """
    #     current_time = ctx.container.time_service.now()
    #     context_str = f"Current time: {current_time.strftime('%Y-%m-%d %H:%M')}"

    #     entities = await ctx.container.ai_service.extract_data(
    #         user_text=ctx.ctx.activity.text,
    #         result_type=ScheduleViewEntities,
    #         prompt_key=PromptKeys.SCHEDULING_VIEW, 
    #         context=context_str
    #     )

    #     return DailyBriefingRequest(
    #         requester_id=ctx.requester_id,
    #         date=entities.date
    #     )

    
    @staticmethod
    def map_to_find_time_view(
        result: SchedulingResult, 
        request: FindTimeRequest
        ) -> FindTimeViewModel:
        """
        Prepares data for the Find Time Adaptive Card.
        Handles both Pydantic models and Dictionaries safely.
        """
        data = result.data
        
        if isinstance(data, dict):
            raw_slots = data.get('slots', [])
            subject = data.get('subject')
            duration = data.get('duration')
        else:
            raw_slots = getattr(data, 'slots', [])
            subject = getattr(data, 'subject', None)
            duration = getattr(data, 'duration', None)

        slots = []
        for slot in raw_slots:
            if isinstance(slot, TimeSlot):
                slots.append(slot)
            elif isinstance(slot, dict):
                slots.append(TimeSlot(**slot))
            else:
                slots.append(slot)

        return FindTimeViewModel(
            slots=slots,
            subject=subject or request.subject,
            participants=result.resolved_participants,
            duration=duration or request.duration_minutes
        )
        
__all__ = (
    "SchedulingMapper",
)

