from pydantic import BaseModel
from typing import List, Generic, TypeVar, Optional, Dict, Any

from schemas.shared import Participant

from .shared import TimeSlot, TimelineSlot


T = TypeVar('T', bound=BaseModel)


class SchedulingResult(BaseModel, Generic[T]):
    """Universal service response for scheduling operations"""
    success: bool
    error: Optional[str] = None
    # Data (filled depending on success)
    data: Optional[T] = None
    # Helper fields to know who we found
    resolved_participants: List[Participant] = []
    
    
class FindTimeDataResponse(BaseModel):
    """Data returned from find time operation"""
    slots: List[TimeSlot]
    subject: str
    duration: int
    participants: List[Participant]


class BookMeetingData(BaseModel):
    """Data returned from booking a meeting"""
    event_id: str
    subject: str
    start_time: str
    end_time: str
    join_url: Optional[str] = None
    organizer: str # Email or Name


class DailyBriefingData(BaseModel):
    """Data returned from daily briefing"""
    events: List[Dict[str, Any]]
    date: str # ISO date
    event_count: int


class ViewScheduleData(BaseModel):
    """Data returned from viewing schedule"""
    events: List[Dict[str, Any]] # Raw graph events
    timeline_slots: List[TimelineSlot]
    date: str # ISO date
    employee_id: str
    employee_name: Optional[str] = None


class UpdateMeetingData(BaseModel):
    """Data returned from updating a meeting"""
    event_id: str
    update_field: str
    new_start_time: Optional[str] = None
    new_end_time: Optional[str] = None


class CancelMeetingData(BaseModel):
    """Data returned from cancelling a meeting"""
    meeting_id: str
    status: str = "Cancelled"  # e.g., "Cancelled"


class CreateWorkshopData(BaseModel):
    """Data returned from creating a workshop"""
    event_id: str
    join_url: Optional[str] = None
    subject: str


__all__ = (
    "SchedulingResult",
    "FindTimeDataResponse",
    "BookMeetingData",
    "DailyBriefingData",
    "ViewScheduleData",
    "UpdateMeetingData",
    "CancelMeetingData",
    "CreateWorkshopData",
)
