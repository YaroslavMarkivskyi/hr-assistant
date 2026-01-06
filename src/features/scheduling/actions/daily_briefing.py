"""
Daily Briefing Action.
Encapsulates logic for retrieving and summarizing daily calendar events.
"""
import logging
from datetime import datetime, timedelta

from services.graph_service import GraphService
from utils.date_parser import parse_date
from ..models import SchedulingResult, DailyBriefingRequest, DailyBriefingData

logger = logging.getLogger("HRBot")


class DailyBriefingAction:
    """
    Action class responsible for fetching daily briefing.
    """

    def __init__(self, graph_service: GraphService):
        self.graph_service = graph_service

    async def execute(
        self, 
        request: DailyBriefingRequest
        ) -> SchedulingResult[DailyBriefingData]:
        """
        Executes the daily briefing logic.
        """
        try:
            # 1. Parse date using global utility
            # If no date provided, use current date
            parsed_date = parse_date(request.date) if request.date else datetime.utcnow()
            
            # Fallback, if parse_date returned None (although it tries not to)
            if not parsed_date:
                parsed_date = datetime.utcnow()
            
            # 2. Calculate Start and End of the day
            # Important: here we reset the time to get the start of the day (00:00:00)
            start_time = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            
            # 3. Call Graph API
            result = await self.graph_service.get_calendar_events(
                user_id=request.requester_id,
                start_time=start_time,
                end_time=end_time,
                include_details=True
            )
            
            if not result.get("success"):
                return SchedulingResult(
                    success=False,
                    error=result.get("error", "Failed to retrieve calendar data")
                )
            
            events = result.get("events", [])
            
            # 4. Wrap response in DTO
            response_data = DailyBriefingData(
                events=events,
                date=parsed_date.isoformat(),
                event_count=len(events)
            )
            
            return SchedulingResult(
                success=True,
                data=response_data
            )
            
        except Exception as e:
            logger.error(f"Error in DailyBriefingAction: {e}", exc_info=True)
            return SchedulingResult(
                success=False,
                error=f"Failed to retrieve briefing: {str(e)}"
            )
            

__all__ = ["DailyBriefingAction"]

