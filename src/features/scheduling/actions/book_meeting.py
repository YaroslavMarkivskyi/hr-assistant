from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from .base import BaseSchedulingAction

from ..schemas import requests as request_schemas
from ..schemas import responses as response_schemas

if TYPE_CHECKING:
    from services.graph_service import GraphService
    from services.user_search import UserSearchService


logger = logging.getLogger(__name__)


class BookMeetingAction(BaseSchedulingAction[
    request_schemas.BookMeetingRequest,
    response_schemas.BookMeetingResponse
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
        request: request_schemas.BookMeetingRequest
    ) -> response_schemas.SchedulingResult[response_schemas.BookMeetingResponse]:
        if request.end_time <= request.start_time:
            return response_schemas.SchedulingResult(
                success=False,
                error="End time must be after start time."
            )
        
        attendee_emails = [
            p.get_email() for p in request.participants if p.get_email()
        ]
        
        result = await self._graph_service.create_meeting(
            organizer_id=request.requester_id,
            attendees=attendee_emails,
            subject=request.subject,
            start_time=request.start_time,
            end_time=request.end_time,
            agenda=request.agenda
        )
        
        if not result.get("success"):
            return response_schemas.SchedulingResult(
                success=False,
                error=result.get("error", "Error creating meeting via Graph API")
            )
            
        event = result.get("event", {})
        response_data = response_schemas.BookMeetingResponse(
            event_id=event.get("id", ""),
            subject=request.subject,
            start_time=request.start_time.isoformat(),
            end_time=request.end_time.isoformat(),
            join_url=event.get("onlineMeeting", {}).get("joinUrl"),
            organizer=event.get("organizer", {}).get("emailAddress", {}).get("name", "Unknown")
        )
        
        return response_schemas.SchedulingResult(
            success=True,
            data=response_data,
            resolved_participants=request.participants
        )

__all__ = (
    "BookMeetingAction",
    )

