from enum import StrEnum


class SchedulingIntent(StrEnum):
    """Scheduling module intents"""
    FIND_TIME = "find_time"  # Smart availability search
    BOOK_MEETING = "book_meeting"  # Create meeting with Teams link
    UPDATE_MEETING = "update_meeting"  # Reschedule meeting
    CANCEL_MEETING = "cancel_meeting"  # Cancel meeting
    CREATE_WORKSHOP = "create_workshop"  # Create workshop/lecture (broadcast mode)
    DAILY_BRIEFING = "daily_briefing"  # "What's on my calendar today?"
    VIEW_SCHEDULE = "view_schedule"  # View employee schedule (Free/Busy or detailed)


__all__ = ("SchedulingIntent",)

