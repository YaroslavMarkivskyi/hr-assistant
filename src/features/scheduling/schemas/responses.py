from pydantic import BaseModel, ConfigDict
from typing import List, Generic, TypeVar, Optional, Dict, Any

from schemas.shared import Participant

from .shared import TimeSlot, TimelineSlot


class BaseSchedulingResponse(BaseModel):
    """Base class for scheduling responses"""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
T = TypeVar('T', bound=BaseSchedulingResponse)


class SchedulingResult(BaseModel, Generic[T]):
    """Universal service response for scheduling operations"""
    success: bool
    error: Optional[str] = None
    # Data (filled depending on success)
    data: Optional[T] = None
    # Helper fields to know who we found
    resolved_participants: List[Participant] = []
    
    
class FindTimeResponse(BaseSchedulingResponse):
    """Data returned from find time operation"""
    slots: List[TimeSlot]
    subject: str
    duration: int
    participants: List[Participant]


class BookMeetingResponse(BaseSchedulingResponse):
    """Data returned from booking a meeting"""
    event_id: str
    subject: str
    start_time: str
    end_time: str
    join_url: Optional[str] = None
    organizer: str # Email or Name


class DailyBriefingResponse(BaseSchedulingResponse):
    """Data returned from daily briefing"""
    events: List[Dict[str, Any]]
    date: str # ISO date
    event_count: int


class ViewScheduleResponse(BaseSchedulingResponse):
    """Data returned from viewing schedule"""
    events: List[Dict[str, Any]] # Raw graph events
    timeline_slots: List[TimelineSlot]
    date: str # ISO date
    employee_id: str
    employee_name: Optional[str] = None


class UpdateMeetingResponse(BaseSchedulingResponse):
    """Data returned from updating a meeting"""
    event_id: str
    update_field: str
    new_start_time: Optional[str] = None
    new_end_time: Optional[str] = None


class CancelMeetingResponse(BaseSchedulingResponse):
    """Data returned from cancelling a meeting"""
    meeting_id: str
    status: str = "Cancelled"  # e.g., "Cancelled"


class CreateWorkshopResponse(BaseSchedulingResponse):
    """Data returned from creating a workshop"""
    event_id: str
    join_url: Optional[str] = None
    subject: str


__all__ = (
    "BaseSchedulingResponse",
    
    "SchedulingResult",
    "FindTimeResponse",
    "BookMeetingResponse",
    "DailyBriefingResponse",
    "ViewScheduleResponse",
    "UpdateMeetingResponse",
    "CancelMeetingResponse",
    "CreateWorkshopResponse",
)

