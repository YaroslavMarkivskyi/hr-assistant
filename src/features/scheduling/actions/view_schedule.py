from __future__ import annotations
import logging

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Optional

from core.utils.date_parser import parse_date

from schemas.shared import Participant

from .base import BaseSchedulingAction

from ..schemas import requests as request_schemas
from ..schemas import responses as response_schemas


if TYPE_CHECKING:
    from services.graph_service import GraphService
    from services.user_search import UserSearchService
    from ..services import TimelineBuilder
    

logger = logging.getLogger(__name__)


class ViewScheduleAction(
    BaseSchedulingAction[
        request_schemas.ViewScheduleRequest,
        response_schemas.ViewScheduleResponse
    ]
):
    def __init__(
        self,
        graph_service: GraphService,
        user_search_service: UserSearchService,
        timeline_builder: TimelineBuilder
    ):
        super().__init__(graph_service)
        self._user_search_service = user_search_service
        self._timeline_builder = timeline_builder
        
    async def _run(
        self,
        request: request_schemas.ViewScheduleRequest
    ) -> response_schemas.SchedulingResult[response_schemas.ViewScheduleResponse]:
        
        target_id = request.target_user_id
        resolved_employee: Optional[Participant] = None
        
        if not target_id and request.employee_name:
            search_result = await self._user_search_service.search_user(request.employee_name)
            
            if search_result.get("success") and search_result.get("user"):
                resolved_employee = search_result["user"]
                target_id = resolved_employee.id
            else:
                return response_schemas.SchedulingResult(
                    success=False,
                    error_message=f"Could not resolve employee name: {request.employee_name}"
                )
        
        if not target_id:
            target_id = request.requester_user_id
            
        parsed_date = parse_date(request.date) if request.date else datetime.now(timezone.utc)
        if not parsed_date:
            parsed_date = datetime.now(timezone.utc)
        
        start_time = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        
        result = await self._graph_service.get_calendar_events(
            user_id=target_id,
            start_time=start_time,
            end_time=end_time,
            include_details=request.detailed
        )
        
        if not result.get("success"):
            return response_schemas.SchedulingResult(
                success=False,
                error_message=result.get("error", "Error retrieving calendar data")
            )
        
        events = result.get("events", [])
        
        timeline_slots = []
        if request.detailed:
            timeline_slots = self._timeline_builder.build(
                events=events,
                day_start=start_time,
                day_end=end_time
            )
            
        employee_display_name = resolved_employee.displayName if resolved_employee else None
        
        response_data = response_schemas.ViewScheduleResponse(
            events=events,
            timeline_slots=timeline_slots,
            date=parsed_date.date().isoformat(),
            employee_id=target_id,
            employee_name=employee_display_name
        )
        
        return response_schemas.SchedulingResult(
            success=True,
            data=response_data,
            resolved_participants=[resolved_employee] if resolved_employee else []
        )
        
        
__all__ = (
    "ViewScheduleAction",
)

