from __future__ import annotations
import logging

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from core.utils.date_parser import parse_date

from .base import BaseSchedulingAction

from ..schemas import requests as request_schemas
from ..schemas import responses as response_schemas

if TYPE_CHECKING:
    from services.graph_service import GraphService
    
    
logger = logging.getLogger(__name__)


class DailyBriefingAction(BaseSchedulingAction[
    request_schemas.DailyBriefingRequest,
    response_schemas.DailyBriefingResponse
]):
    async def _run(
        self,
        request: request_schemas.DailyBriefingRequest
    ) -> response_schemas.SchedulingResult[response_schemas.DailyBriefingResponse]:
        parsed_date = parse_date(request.date) if request.date else datetime.now(timezone.utc)
        
        if not parsed_date:
            parsed_date = datetime.now(timezone.utc)
            
        start_time = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        
        result = await self._graph_service.get_calendar_events(
            user_id=request.requester_id,
            start_time=start_time,
            end_time=end_time,
            include_details=True
        )
        
        if not result.get("success"):
            return response_schemas.SchedulingResult(
                success=False,
                error=result.get("error", "Failed to retrieve calendar data")
            )
            
        events = result.get("events", [])
        
        response_data = response_schemas.DailyBriefingResponse(
            events=events,
            date=parsed_date.isoformat(),
            event_count=len(events)
        )
        
        return response_schemas.SchedulingResult(
            success=True,
            data=response_data
        )
        
__all__ = (
    "DailyBriefingAction",
    )

