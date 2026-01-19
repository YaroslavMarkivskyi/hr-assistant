from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Any, Union

from datetime import datetime

from schemas.shared import Participant


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


__all__ = (
    "TimeSlot",
    "TimelineSlot",
    "BookSlotContext",
    "ShowMoreSlotsContext",
    )

