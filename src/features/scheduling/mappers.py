import logging

from core.enums.prompts import PromptKeys
from features.scheduling.schemas import (
    FindTimeRequest, 
    ViewScheduleRequest, 
    CancelMeetingRequest, 
    DailyBriefingRequest,
    IntentContext,
    SchedulingResult,
    TimeSlot,
    FindTimeViewModel
)
from schemas.ai.scheduling import (
    ScheduleQueryEntities, 
    ScheduleViewEntities, 
    ScheduleCancelEntities
)

logger = logging.getLogger("HRBot")

class SchedulingMapper:
    """
    Responsible for converting:
    1. Raw User Text -> Structured Service Requests (via AI)
    2. Service Results -> UI View Models (for Adaptive Cards)
    """

    # =========================================================================
    # REQUEST MAPPERS (Text -> Data)
    # =========================================================================

    @staticmethod
    async def map_to_find_time_request(ctx: IntentContext) -> FindTimeRequest:
        """Extracts meeting details using AI."""
        current_time = ctx.container.time_service.now()
        context_str = f"Current time: {current_time.strftime('%Y-%m-%d %H:%M')}"

        entities = await ctx.container.ai_service.extract_data(
            user_text=ctx.ctx.activity.text,
            result_type=ScheduleQueryEntities,
            prompt_key=PromptKeys.SCHEDULING_EXTRACT,
            context=context_str
        )
        
        logger.info(f"[Mapper] Extracted FindTime entities: {entities}")

        # 2. Mapping to DTO
        return FindTimeRequest(
            requester_id=ctx.requester_id,
            subject=entities.subject or "Meeting",
            participant_names=entities.participants,
            duration_minutes=entities.duration_minutes or 30,
            start_date=entities.date,
            time_preference=entities.specific_time or entities.day_part
        )

    @staticmethod
    async def map_to_view_schedule_request(ctx: IntentContext) -> ViewScheduleRequest:
        """Extracts target person and date."""
        current_time = ctx.container.time_service.now()
        context_str = f"Current time: {current_time.strftime('%Y-%m-%d %H:%M')}"

        entities = await ctx.container.ai_service.extract_data(
            user_text=ctx.ctx.activity.text,
            result_type=ScheduleViewEntities,
            prompt_key=PromptKeys.SCHEDULING_VIEW,
            context=context_str
        )

        current_user_name = ctx.ctx.activity.from_property.name
        is_self = entities.target_person is None
        
        return ViewScheduleRequest(
            requester_id=ctx.requester_id,
            target_employee_name=current_user_name if is_self else entities.target_person,
            target_employee_id=ctx.requester_id if is_self else None, 
            date=entities.date,
            detailed=True
        )

    @staticmethod
    async def map_to_cancel_request(ctx: IntentContext) -> CancelMeetingRequest:
        """Extracts keywords to identify meeting to cancel."""
        current_time = ctx.container.time_service.now()
        context_str = f"Current time: {current_time.strftime('%Y-%m-%d %H:%M')}"

        entities = await ctx.container.ai_service.extract_data(
            user_text=ctx.ctx.activity.text,
            result_type=ScheduleCancelEntities,
            prompt_key=PromptKeys.SCHEDULING_CANCEL,
            context=context_str
        )
        
        return CancelMeetingRequest(
            requester_id=ctx.requester_id,
            keywords=entities.subject_keywords,
            participants=entities.participants,
            target_date=entities.date
        )

    @staticmethod
    async def map_to_daily_briefing_request(ctx: IntentContext) -> DailyBriefingRequest:
        """
        Extracts date for briefing (e.g., 'briefing for tomorrow').
        Uses the same prompt as View Schedule because semantics are similar.
        """
        current_time = ctx.container.time_service.now()
        context_str = f"Current time: {current_time.strftime('%Y-%m-%d %H:%M')}"

        entities = await ctx.container.ai_service.extract_data(
            user_text=ctx.ctx.activity.text,
            result_type=ScheduleViewEntities,
            prompt_key=PromptKeys.SCHEDULING_VIEW, 
            context=context_str
        )

        return DailyBriefingRequest(
            requester_id=ctx.requester_id,
            date=entities.date
        )

    # =========================================================================
    # VIEW MAPPERS (Data -> UI)
    # =========================================================================

    @staticmethod
    def map_to_find_time_view(result: SchedulingResult, request: FindTimeRequest) -> FindTimeViewModel:
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
            elif hasattr(slot, 'model_dump'):
                slots.append(TimeSlot(**slot.model_dump()))
            else:
                slots.append(slot)

        final_subject = subject or request.subject
        final_duration = duration or request.duration_minutes
        
        return FindTimeViewModel(
            slots=slots,
            subject=final_subject,
            participants=result.resolved_participants,
            duration=final_duration
        )