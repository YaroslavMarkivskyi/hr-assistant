"""
View Schedule Action.
Encapsulates logic for resolving users, fetching calendar, and building timelines.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from services.graph_service import GraphService
from services.user_search import UserSearchService
from core.utils.date_parser import parse_date
from ..schemas import (
    SchedulingResult, 
    Participant, 
    ViewScheduleRequest, 
    ViewScheduleData
)
from ..services.timeline import TimelineBuilder

logger = logging.getLogger("HRBot")


class ViewScheduleAction:
    """
    Action class responsible for viewing employee schedules.
    """

    def __init__(
        self, 
        graph_service: GraphService, 
        user_search_service: UserSearchService,
        timeline_builder: TimelineBuilder
    ):
        self.graph_service = graph_service
        self.user_search_service = user_search_service
        self.timeline_builder = timeline_builder

    async def execute(self, request: ViewScheduleRequest) -> SchedulingResult[ViewScheduleData]:
        try:
            # 1. Resolve Target User
            target_id = request.employee_id
            resolved_employee: Optional[Participant] = None
            
            # If no ID, try to resolve by name
            if not target_id and request.employee_name:
                search_result = await self.user_search_service.search_user(request.employee_name)
                
                if search_result.get("success") and search_result.get("user"):
                    user = search_result["user"]
                    target_id = user.get("id")
                    
                    resolved_employee = Participant(
                        id=user.get("id"),
                        displayName=user.get("displayName"),
                        mail=user.get("mail"),
                        userPrincipalName=user.get("userPrincipalName"),
                        givenName=user.get("givenName"),
                        surname=user.get("surname")
                    )
                else:
                    return SchedulingResult(
                        success=False,
                        error=f"Could not find user '{request.employee_name}'. Please check the name."
                    )
            
            # If nothing was provided, show the schedule of the requester (self)
            if not target_id:
                target_id = request.requester_id

            # 2. Parse Date
            parsed_date = parse_date(request.date) if request.date else datetime.utcnow()
            if not parsed_date:
                parsed_date = datetime.utcnow()
            
            # 3. Calculate Day Boundaries
            start_time = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            
            # 4. Fetch Events from Graph
            result = await self.graph_service.get_calendar_events(
                user_id=target_id,
                start_time=start_time,
                end_time=end_time,
                include_details=request.detailed
            )
            
            if not result.get("success"):
                return SchedulingResult(
                    success=False,
                    error=result.get("error", "Error fetching schedule")
                )
            
            events = result.get("events", [])
            
            # 5. Build Timeline (Domain Logic)
            timeline_slots = []
            if request.detailed:
                timeline_slots = self.timeline_builder.build(
                    events=events,
                    day_start=start_time,
                    day_end=end_time
                )
            
            # 6. Prepare Response DTO
            employee_display_name = resolved_employee.get_display_name() if resolved_employee else None
            
            response_data = ViewScheduleData(
                events=events,
                timeline_slots=timeline_slots,
                date=parsed_date.isoformat(),
                employee_id=target_id,
                employee_name=employee_display_name
            )
            
            return SchedulingResult(
                success=True,
                data=response_data,
                resolved_participants=[resolved_employee] if resolved_employee else []
            )
            
        except Exception as e:
            logger.error(f"Error in ViewScheduleAction: {e}", exc_info=True)
            return SchedulingResult(
                success=False,
                error=f"Error viewing schedule: {str(e)}"
            )
            
__all__ = ["ViewScheduleAction"]

