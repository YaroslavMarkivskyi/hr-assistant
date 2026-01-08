from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ScheduleQueryEntities(BaseModel):
    """
    Entities extracted from scheduling-related user queries.
    """
    participants: List[str] = Field(
        default_factory=list,
        description="List of person names extracted from text (e.g. 'with Anton', 'and Anna'). Exclude 'me'."
    )
    subject: str = Field(
        default="Meeting",
        description="Subject or title of the meeting (e.g. 'Project Sync', '1:1 with Manager'). Default is 'Meeting'."
    )
    date: Optional[str] = Field(
        default=None,
        description="Date in YYYY-MM-DD format. Calculate relative dates (tomorrow, next Friday) based on CONTEXT."
    )    
    duration_minutes: int = Field(
        default=30,
        description="Duration in minutes. Convert 'hour' to 60, 'half hour' to 30. Default is 30."
    )
    specific_time: Optional[str] = Field(
        default=None,
        description="Specific start time in HH:MM format (24h) if mentioned explicitly (e.g. 'at 18:00', 'at 2pm')."
    )
    day_part: Optional[Literal['morning', 'afternoon', 'evening', 'end_of_day']] = Field(
        default=None,
        description="Vague time preference. Use 'morning' for before 12:00, 'afternoon' for 12:00-17:00, etc."
    )
    

class ScheduleViewEntities(BaseModel):
    """
    Entities extracted from schedule viewing-related user queries.
    """
    target_person: Optional[str] = Field(
        default=None,
        description=(
            "Name of the person whose schedule to view (e.g. 'Alice', 'Brown'). "
            "IMPORTANT: If the user refers to themselves (e.g. 'my schedule', 'for me', 'Show schedule'), "
            "this field MUST be None."
        )
    )
    date: Optional[str] = Field(
        default=None,
        description=(
            "Date in YYYY-MM-DD format for which the schedule is requested."
            "Calculate relative dates (today, tomorrow, next Monday) based on CONTEXT."
            "If not specified, defaults to today."
        )
    )
    
    
class ScheduleCancelEntities(BaseModel):
    """
    Entities extracted from meeting cancellation-related user queries.
    """
    date: Optional[str] = Field(
        default=None,
        description=(
            "Date in YYYY-MM-DD format of the meeting to cancel."
            "Calculate relative dates (today, tomorrow, next Monday) based on CONTEXT."
            "If not specified, defaults to today."
        )
    )   
    start_time: Optional[str] = Field(
        default=None,
        description="Start time in HH:MM format (24h) of the meeting to cancel."
    )
    participants: List[str] = Field(
        default_factory=list,
        description="List of person names involved in the meeting to cancel (e.g. 'with Anton', 'and Anna'). Exclude 'me'."
    )
    subject_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords from the meeting subject/title to help identify the meeting (e.g. 'project sync', '1:1')."
    )
    reason: Optional[str] = Field(
        default=None,
        description="Reason for cancellation if provided (e.g. 'due to illness', 'because of a conflict')."   
    )
    

class UpdateMeetingEntities(BaseModel):
    """
    Entities extracted from meeting update-related user queries.
    """
    date: Optional[str] = Field(
        default=None,
        description=(
            "Date in YYYY-MM-DD format of the meeting to update."
            "Calculate relative dates (today, tomorrow, next Monday) based on CONTEXT."
            "If not specified, defaults to today or nearest future date."
        )
    )   
    start_time: Optional[str] = Field(
        default=None,
        description="Start time in HH:MM format (24h) of the meeting to update."
    )
    subject_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords from the meeting subject/title to help identify the meeting (e.g. 'project sync', '1:1')."
    )
    new_date: Optional[str] = Field(
        default=None,
        description="New date in YYYY-MM-DD format if the meeting date is to be changed."
    )
    new_time: Optional[str] = Field(
        default=None,
        description="New start time in HH:MM format (24h) if the meeting time is to be changed."
    )
    participants: List[str] = Field(
        default_factory=list,
        description="List of person names involved in the meeting to update (e.g. 'with Anton', 'and Anna'). Exclude 'me'."
    )
    new_duration_minutes: Optional[int] = Field(
        default=None,
        description="New duration in minutes if the meeting duration is to be changed."
    )
    
    

__all__ = [
    "ScheduleQueryEntities",
    "ScheduleViewEntities",
    "ScheduleCancelEntities",
    "UpdateMeetingEntities"
    ]