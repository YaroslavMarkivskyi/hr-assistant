"""
User intent types that the bot recognizes

This file contains only intent enum definitions.
All intents are organized by modules for better IDE autocomplete.
"""
from enum import StrEnum
from typing import Union


# ============================================================================
# Module-Specific Intents (Sources of Truth)
# ============================================================================

class SchedulingIntent(StrEnum):
    """Scheduling module intents"""
    FIND_TIME = "find_time"  # Smart availability search
    BOOK_MEETING = "book_meeting"  # Create meeting with Teams link
    UPDATE_MEETING = "update_meeting"  # Reschedule meeting
    CANCEL_MEETING = "cancel_meeting"  # Cancel meeting
    CREATE_WORKSHOP = "create_workshop"  # Create workshop/lecture (broadcast mode)
    DAILY_BRIEFING = "daily_briefing"  # "What's on my calendar today?"
    VIEW_SCHEDULE = "view_schedule"  # View employee schedule (Free/Busy or detailed)


class GeneralIntent(StrEnum):
    """General intents (not tied to any specific module)"""
    CHAT = "chat"
    UNKNOWN = "unknown"  # When LLM cannot determine the intent


# ============================================================================
# Type Alias for Type Hinting
# ============================================================================

# Union type for all intents (used for type hints)
AnyIntent = Union[
    SchedulingIntent,
    GeneralIntent
]

# Alias for backward compatibility (deprecated, use AnyIntent)
BotIntent = Union[
    SchedulingIntent,
    GeneralIntent
]

