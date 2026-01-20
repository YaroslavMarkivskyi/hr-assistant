from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union
from datetime import datetime

from schemas.shared import Participant


class BaseSchedulingRequest(BaseModel):
    """Base class for scheduling requests"""
    requester_id: str
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
        )


class FindTimeRequest(BaseSchedulingRequest):
    """Request model for finding meeting times"""
    participant_names: List[str]
    subject: str = "Meeting"
    duration_minutes: int = 30
    start_date: Optional[Union[str, datetime]] = None
    end_date: Optional[Union[str, datetime]] = None
    

class BookMeetingRequest(BaseSchedulingRequest):
    """Request model for booking a meeting"""
    subject: str
    participants: List[Participant]
    start_time: datetime
    end_time: datetime
    agenda: Optional[str] = None


class ViewScheduleRequest(BaseSchedulingRequest):
    """Request model for viewing schedule"""
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    date: Optional[Union[str, datetime]] = None
    detailed: bool = False

class DailyBriefingRequest(BaseSchedulingRequest):
    """Request model for daily briefing"""
    date: Optional[Union[str, datetime]] = None


class UpdateMeetingRequest(BaseSchedulingRequest):
    """Request model for updating a meeting"""
    meeting_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    subject: Optional[str] = None
    participants: Optional[List[Participant]] = None


class CancelMeetingRequest(BaseSchedulingRequest):
    """Request model for cancelling a meeting"""
    meeting_id: str
    comment: Optional[str] = None


class CreateWorkshopRequest(BaseSchedulingRequest):
    """Request model for creating a workshop"""
    subject: str
    participants: List[Participant]
    start_time: datetime
    end_time: datetime
    ignore_availability: bool = False


__all__ = (
    "BaseSchedulingRequest",
    
    "FindTimeRequest",
    "BookMeetingRequest",
    "ViewScheduleRequest",
    "DailyBriefingRequest",
    "UpdateMeetingRequest",
    "CancelMeetingRequest",
    "CreateWorkshopRequest",
    )

