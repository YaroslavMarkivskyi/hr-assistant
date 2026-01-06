"""
Request Mappers for Scheduling Module.

Responsible for converting raw inputs (AI Entities, Action Payloads) 
into strongly typed Request DTOs.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from models.ai import AIResponse
from .models import (
    FindTimeRequest, 
    BookMeetingRequest, 
    Participant,
    SchedulingResult,
    TimeSlot,
    ViewScheduleRequest,
    DailyBriefingRequest,
    IntentContext,
    FindTimeViewModel
)

logger = logging.getLogger("HRBot")


class SchedulingMapper:
    """
    Static utility class for mapping inputs to Scheduling DTOs.
    """

    @staticmethod
    def map_find_time_intent(context: IntentContext) -> FindTimeRequest:
        """
        Maps IntentContext -> FindTimeRequest.
        """
        entities = context.ai_response.entities or {}
        
        logger.info(f"🧠 [Mapper] RAW ENTITIES from AI: {entities}")
        
        raw_participants = (
            entities.get("participants") or 
            entities.get("person") or 
            entities.get("people") or 
            []
        )
        
        names = SchedulingMapper._extract_names(raw_participants)
        
        logger.info(f"🧩 [Mapper] Extracted names: {names}")
        
        return FindTimeRequest(
            requester_id=context.requester_id,
            participant_names=names,
            subject=entities.get("subject", "Meeting"),
            duration_minutes=int(entities.get("duration", 30)),
            start_date=entities.get("date"), 
            end_date=entities.get("endDate")
        )

    @staticmethod
    def map_view_schedule_request(requester_id: str, ai_response: AIResponse) -> ViewScheduleRequest:
        """
        Maps AI response entities to ViewScheduleRequest DTO.
        """
        entities = ai_response.entities or {}
        
        return ViewScheduleRequest(
            requester_id=requester_id,
            employee_id=entities.get("employee_id"),
            employee_name=entities.get("person") or entities.get("employee_name"),
            date=entities.get("date"),
            detailed=True
        )

    @staticmethod
    def map_daily_briefing_request(requester_id: str, ai_response: AIResponse) -> DailyBriefingRequest:
        """
        Maps AI response entities to DailyBriefingRequest DTO.
        """
        entities = ai_response.entities or {}
        return DailyBriefingRequest(
            requester_id=requester_id,
            date=entities.get("date")
        )

    # --- Helpers ---

    @staticmethod
    def _extract_names(raw_data: Any) -> List[str]:
        """
        Robustly extracts names from various input formats (str, list of strs, list of dicts).
        """
        names = []
        
        if isinstance(raw_data, str):
            if raw_data.strip():
                return [raw_data.strip()]
            return []
            
        if isinstance(raw_data, list):
            for item in raw_data:
                if isinstance(item, str):
                    if item.strip():
                        names.append(item.strip())
                elif isinstance(item, dict):
                    name = (
                        item.get("name") or 
                        item.get("text") or 
                        item.get("value") or 
                        item.get("person")
                    )
                    if name and isinstance(name, str):
                        names.append(name.strip())
        
        return names
    
    @staticmethod
    def map_to_find_time_view(result: SchedulingResult, request: FindTimeRequest) -> Dict[str, Any]:
        """
        Prepares data for the Find Time Adaptive Card.
        Handles type conversions (dict -> TimeSlot) and fallbacks.
        Returns a dictionary ready to be unpacked into create_find_time_card.
        """
        data = result.data
        
        slots = []
        raw_slots = getattr(data, 'slots', []) or []
        
        for slot in raw_slots:
            if isinstance(slot, dict):
                slots.append(TimeSlot(**slot))
            else:
                slots.append(slot)

        subject = getattr(data, 'subject', None) or request.subject
        duration = getattr(data, 'duration', None) or request.duration_minutes
        
        return FindTimeViewModel(
            slots=slots,
            subject=subject,
            participants=result.resolved_participants,
            duration=duration
        )
    

__all__ = ["SchedulingMapper"]

