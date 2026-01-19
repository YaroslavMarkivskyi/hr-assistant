from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from schemas.shared import Participant
from .shared import TimeSlot


class FindTimeViewModel(BaseModel):
    """View model for Find Time results"""
    slots: List[TimeSlot]
    subject: str
    participants: List[Participant]
    duration: int


class ScheduleViewModel(BaseModel):
    employee_name: str
    date_str: str
    grouped_slots: List[Dict[str, Any]]


class DailyBriefingViewModel(BaseModel):
    date_str: str
    meetings_count: int
    next_meeting_text: Optional[str] = None
    free_windows_text: Optional[str] = None


class BookingConfirmationViewModel(BaseModel):
    subject: str
    participants: List[Participant]
    duration: int
    start_time_str: Optional[str] = None
    agenda: Optional[str] = None


__all__ = (
    "FindTimeViewModel",
    "ScheduleViewModel",
    "DailyBriefingViewModel",
    "BookingConfirmationViewModel",
)

