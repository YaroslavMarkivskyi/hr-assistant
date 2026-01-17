"""
Book Meeting Action.
Encapsulates logic for creating calendar events.
"""
import logging
from ..schemas import SchedulingResult, BookMeetingRequest, BookMeetingData

logger = logging.getLogger("HRBot")

class BookMeetingAction:
    def __init__(self, graph_service):
        self.graph_service = graph_service

    async def execute(self, request: BookMeetingRequest) -> SchedulingResult[BookMeetingData]:
        try:
            # 1. Validation of input
            if request.end_time <= request.start_time:
                return SchedulingResult(
                    success=False, 
                    error="End time must be after start time."
                )

            # 2. Prepare data
            attendee_emails = [
                p.get_email() for p in request.participants if p.get_email()
            ]
            
            # 3. Call API
            result = await self.graph_service.create_meeting(
                organizer_id=request.requester_id,
                attendees=attendee_emails,
                subject=request.subject,
                start_time=request.start_time,
                end_time=request.end_time,
                agenda=request.agenda
            )
            
            if not result.get("success"):
                return SchedulingResult(
                    success=False,
                    error=result.get("error", "Error creating meeting")
                )
            
            # 4. Map result to strict object
            event = result.get("event", {})
            response_data = BookMeetingData(
                event_id=event.get("id", ""),
                subject=request.subject,
                start_time=request.start_time.isoformat(),
                end_time=request.end_time.isoformat(),
                join_url=event.get("onlineMeeting", {}).get("joinUrl"),
                organizer=event.get("organizer", {}).get("emailAddress", {}).get("name", "Unknown")
            )
            
            return SchedulingResult(
                success=True,
                data=response_data,
                resolved_participants=request.participants
            )

        except Exception as e:
            logger.error(f"Error in BookMeetingAction: {e}", exc_info=True)
            return SchedulingResult(success=False, error=str(e))
        

__all__ = ["BookMeetingAction"]

