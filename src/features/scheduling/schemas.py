"""
Data models for Scheduling module.

Uses Pydantic for data validation and serialization.
"""
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Any, Dict, List, Optional, Literal, Union, Generic, TypeVar
from datetime import datetime
from schemas.bot import ActionPayload
from bot.activity_context_wrapper import ActivityContextWrapper
from schemas.ai import UserIntent

T = TypeVar('T', bound=BaseModel)


class Participant(BaseModel):
    """Participant in a meeting or scheduling operation"""
    id: Optional[str] = None  # Azure AD Object ID
    displayName: Optional[str] = None  # Full display name
    mail: Optional[str] = None  # Email address
    userPrincipalName: Optional[str] = None  # UPN (user@domain.com)
    givenName: Optional[str] = None  # First name
    surname: Optional[str] = None  # Last name
    email: Optional[str] = None  # Alias for mail or userPrincipalName
    
    def get_email(self) -> Optional[str]:
        """Get email address (mail, userPrincipalName, or email field)"""
        return self.mail or self.userPrincipalName or self.email
    
    def get_display_name(self) -> str:
        """Get display name or fallback to email"""
        return self.displayName or self.get_email() or "Unknown"


class TimeSlot(BaseModel):
    """Time slot for meeting availability"""
    start_time: str
    end_time: str
    confidence: str = "medium"
    busy_participants: Optional[List[Participant]] = None


class TimelineSlot(BaseModel):
    """Single slot in employee schedule timeline"""
    time_range: str  # "09:00 - 10:00"
    status: Literal["busy", "available", "ooo"]
    subject: str
    start: datetime
    end: datetime


class MeetingData(BaseModel):
    """Meeting data for booking"""
    subject: str
    participants: List[Participant]
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: int
    agenda: Optional[str] = None


class ScheduleGroup(BaseModel):
    """Grouped consecutive slots with same status"""
    start: str
    end: str
    status: Literal["busy", "available", "ooo"]
    subject: str


class FindTimeData(BaseModel):
    """Data returned from find time operation"""
    slots: List[TimeSlot]
    subject: str
    duration: int
    participants: List[Participant]


# Universal service response for scheduling operations
class SchedulingResult(BaseModel, Generic[T]):
    """Universal service response for scheduling operations"""
    success: bool
    error: Optional[str] = None
    
    # Data (filled depending on success)
    data: Optional[T] = None
    
    # Helper fields to know who we found
    resolved_participants: List[Participant] = []


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
    participants: List['Participant']
    start_time: datetime
    end_time: datetime
    agenda: Optional[str] = None


class BookMeetingData(BaseModel):
    """Data returned from booking a meeting"""
    event_id: str
    subject: str
    start_time: str
    end_time: str
    join_url: Optional[str] = None
    organizer: str # Email or Name
    

class DailyBriefingRequest(BaseModel):
    """Request model for daily briefing"""
    requester_id: str
    date: Optional[Union[str, datetime]] = None
    
    
class DailyBriefingData(BaseModel):
    """Data returned from daily briefing"""
    events: List[Dict[str, Any]]
    date: str # ISO date
    event_count: int
    
    
class ViewScheduleRequest(BaseModel):
    """Request model for viewing schedule"""
    requester_id: str
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    date: Optional[Union[str, datetime]] = None
    detailed: bool = False
    

class ViewScheduleData(BaseModel):
    """Data returned from viewing schedule"""
    events: List[Dict[str, Any]] # Raw graph events
    timeline_slots: List[TimelineSlot]
    date: str # ISO date
    employee_id: str
    employee_name: Optional[str] = None
    
    
class UpdateMeetingRequest(BaseModel):
    """Request model for updating a meeting"""
    requester_id: str
    meeting_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    subject: Optional[str] = None
    participants: Optional[List[Participant]] = None
    

class UpdateMeetingData(BaseModel):
    """Data returned from updating a meeting"""
    event_id: str
    update_field: str
    new_start_time: Optional[str] = None
    new_end_time: Optional[str] = None
    

class CancelMeetingRequest(BaseModel):
    """Request model for cancelling a meeting"""
    requester_id: str
    meeting_id: str
    comment: Optional[str] = None
    
    
class CancelMeetingData(BaseModel):
    """Data returned from cancelling a meeting"""
    meeting_id: str
    status: str = "Cancelled"  # e.g., "Cancelled"
    

class CreateWorkshopRequest(BaseModel):
    """Request model for creating a workshop"""
    requester_id: str
    subject: str
    participants: List[Participant]
    start_time: datetime
    end_time: datetime
    ignore_availability: bool = False
    

class CreateWorkshopData(BaseModel):
    """Data returned from creating a workshop"""
    event_id: str
    join_url: Optional[str] = None
    subject: str
    

class BaseContext(BaseModel):
    """Base context model for scheduling operations"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    requester_id: str
    ctx: ActivityContextWrapper
    container: Any  # ServiceContainer
    
    
class IntentContext(BaseContext):
    """Context model for intent handling"""
    user_intent: UserIntent
    

class ActionContext(BaseContext):
    """Context model for action execution"""
    payload: ActionPayload
    

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
    

class BookSlotContext(BaseModel):
    """Context model for booking a slot action"""
    start: datetime
    end: datetime
    subject: str
    duration: int
    participants: List[Participant] = Field(default_factory=list)
    agenda: Optional[str] = None
    
@field_validator("start", "end", mode="before")
@classmethod
def parse_datetime(cls, v: Any) -> str:
    "Auto-convert ISO strings to datetime objects"
    if isinstance(v, datetime):
        return v
    
    if isinstance(v, str):
        try:
            clean_v = v.replace("Z", "+00:00")
            return datetime.fromisoformat(clean_v)
        except ValueError:
            raise ValueError(f"Invalid datetime string: {v}")
    raise ValueError(f"Unsupported type for datetime field: {type(v)}")


class ShowMoreSlotsContext(BaseModel):
    """Context model for showing more slots action"""
    subject: str
    duration: int
    next_page_date: datetime
    participants: List[Participant] = Field(default_factory=list)
    
    @field_validator("next_page_date", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime:
        if isinstance(v, str):
            try:
                clean_v = v.replace("Z", "+00:00")
                return datetime.fromisoformat(clean_v)
            except ValueError:
                raise ValueError(f"Invalid datetime string: {v}")