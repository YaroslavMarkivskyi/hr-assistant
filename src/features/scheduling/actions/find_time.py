from __future__ import annotations
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Union, Dict, Tuple, TYPE_CHECKING

from core.utils.date_parser import parse_date

from .base import BaseSchedulingAction

from ..schemas import requests as request_schemas
from ..schemas import responses as response_schemas
from ..schemas.shared import TimeSlot

from schemas.shared import (
    Participant,
)




if TYPE_CHECKING:
    from services.graph_service import GraphService
    from services.user_search import UserSearchService


logger = logging.getLogger(__name__)


class FindTimeAction(BaseSchedulingAction[
    request_schemas.FindTimeRequest,
    response_schemas.FindTimeResponse
]):
    def __init__(
        self,
        graph_service: GraphService,
        user_search_service: UserSearchService
    ):
        super().__init__(graph_service)
        self._user_search_service = user_search_service

    async def _run(
        self,
        request: request_schemas.FindTimeRequest
    ) -> response_schemas.SchedulingResult[response_schemas.FindTimeResponse]:
        
        search_start, search_end = self._get_search_window(
            request.start_date,
            request.end_date
        )
        
        resolved_participants = await self._resolve_participants(request.participant_names)
        
        participant_emails = [
            p.get_email() for p in resolved_participants if p.get_email()
        ]
        
        if not participant_emails:
            return response_schemas.SchedulingResult(
                success=False,
                error="Did not find any participants with valid email.",
                resolved_participants=resolved_participants
            )
        
        result = await self._graph_service.find_free_slots(
            organizer_id=request.requester_id,
            user_emails=participant_emails,
            start_date=search_start,
            end_date=search_end,
            duration_minutes=request.duration_minutes
        )
        
        if not result.get("success"):
            return response_schemas.SchedulingResult(
                success=False,
                error=result.get("error", "Error finding free slots"),
                resolved_participants=resolved_participants
            )
            
        slots = self._map_suggestions_to_slots(
            suggestions=result.get("suggestions", []),
            resolved_participants=resolved_participants
        )
        
        if not slots:
            return response_schemas.SchedulingResult(
                success=False,
                error="No free time found for all participants.",
                resolved_participants=resolved_participants
            )
            
        response_data = response_schemas.FindTimeResponse(
            slots=slots,
            subject=request.subject,
            duration=request.duration_minutes,
            participants=resolved_participants
        )
        
        return response_schemas.SchedulingResult(
            success=True,
            data=response_data,
            resolved_participants=resolved_participants
        )
        
    def _get_search_window(
        self,
        start: Optional[Union[str, datetime]],
        end: Optional[Union[str, datetime]]
    ) -> Tuple[datetime, datetime]:
        parsed_start = parse_date(start) if start else None
        
        if not parsed_start:
            parsed_start = datetime.utcnow()
            
        parsed_end = parse_date(end) if end else None
        
        if not parsed_end:
            parsed_end = parsed_start + timedelta(days=7)
            
        return parsed_start, parsed_end

    async def _resolve_participants(self, names: List[str]) -> List[Participant]:
        resolved = []
        
        for name in names:
            try:
                search_result = await self._user_search_service.search_user(name)
                
                if search_result.get("success") and search_result.get("user"):
                    user = search_result["user"]
                    resolved.append(Participant(
                        id=user.get("id"),
                        displayName=user.get("displayName"),
                        mail=user.get("mail"),
                        userPrincipalName=user.get("userPrincipalName"),
                        givenName=user.get("givenName"),
                        surname=user.get("surname")
                    ))
                elif "@" in name:
                    resolved.append(Participant(
                        displayName=name,
                        mail=name,
                        email=name
                    ))
                else:
                    logger.warning(f"Dropping unresolved participant: {name}")
            except Exception as e:
                logger.error(f"Exception searching for participant '{name}': {e}", exc_info=True)
        return resolved
    
    def _map_suggestions_to_slots(
        self,
        suggestions: List[Dict],
        resolved_participants: List[Participant]
    ) -> List[TimeSlot]:
        slots = []
        
        for suggestion in suggestions:
            meeting_time = suggestion.get("meetingTimeSlot", {})
            start = meeting_time.get("start", {}).get("dateTime")
            end = meeting_time.get("end", {}).get("dateTime")
            
            if not start or not end:
                continue

            busy_people = []
            attendee_availability = suggestion.get("attendeeAvailability", [])
            
            for attendee in attendee_availability:
                availability = attendee.get("availability")
                if availability in ["busy", "tentative", "oof"]:
                    email = attendee.get("emailAddress", {}).get("address", "")
                    
                    participant = next(
                        (p for p in resolved_participants if p.get_email() and p.get_email().lower() == email.lower()),
                        Participant(displayName=email, mail=email, email=email)
                    )
                    if participant:
                        busy_people.append(participant)
            
            slots.append(TimeSlot(
                start_time=start,
                end_time=end,
                confidence=str(suggestion.get("confidence", "medium")),
                busy_participants=busy_people if busy_people else None
            ))
            
        return slots

    
__all__ = ["FindTimeAction"]

