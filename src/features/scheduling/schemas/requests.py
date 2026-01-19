from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

from schemas.shared import Participant


class FindTimeRequest(BaseModel):
    """Request model for finding meeting times"""
    requester_id: str
    participant_names: List[str]
    subject: str = "Meeting"
    duration_minutes: int = 30
    start_date: Optional[Union[str, datetime]] = None
    end_date: Optional[Union[str, datetime]] = None
    

class BookMeetingRequest(BaseModel):
    """Request model for booking a meeting"""
    requester_id: str
    subject: str
    participants: List[Participant]
    start_time: datetime
    end_time: datetime
    agenda: Optional[str] = None


class ViewScheduleRequest(BaseModel):
    """Request model for viewing schedule"""
    requester_id: str
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    date: Optional[Union[str, datetime]] = None
    detailed: bool = False

class DailyBriefingRequest(BaseModel):
    """Request model for daily briefing"""
    requester_id: str
    date: Optional[Union[str, datetime]] = None


class UpdateMeetingRequest(BaseModel):
    """Request model for updating a meeting"""
    requester_id: str
    meeting_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    subject: Optional[str] = None
    participants: Optional[List[Participant]] = None


class CancelMeetingRequest(BaseModel):
    """Request model for cancelling a meeting"""
    requester_id: str
    meeting_id: str
    comment: Optional[str] = None


class CreateWorkshopRequest(BaseModel):
    """Request model for creating a workshop"""
    requester_id: str
    subject: str
    participants: List[Participant]
    start_time: datetime
    end_time: datetime
    ignore_availability: bool = False


__all__ = (
    "FindTimeRequest",
    "BookMeetingRequest",
    "ViewScheduleRequest",
    "DailyBriefingRequest",
    "UpdateMeetingRequest",
    "CancelMeetingRequest",
    "CreateWorkshopRequest",
    )

