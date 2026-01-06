"""
Scheduling Feature - Public API

Package by Feature structure:
- controller.py: Thin controller - routes intents/actions, orchestrates flow
- service.py: Business logic layer - all scheduling operations
- models.py: Data models - Pydantic models for type safety
- views.py: UI layer - Adaptive Card rendering

Note: SchedulingController is imported lazily in container.py to avoid circular dependencies.
"""
from .service import SchedulingService
from .models import (
    Participant,
    SchedulingResult,
    TimeSlot,
    TimelineSlot,
    MeetingData,
    ScheduleGroup,
)

__all__ = [
    "SchedulingService",
    "Participant",
    "SchedulingResult",
    "TimeSlot",
    "TimelineSlot",
    "MeetingData",
    "ScheduleGroup",
]

