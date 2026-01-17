"""
User intent types that the bot recognizes

This file contains only intent enum definitions (Sources of Truth).
No logic, no mappings - just pure enum definitions.
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


class TimeOffIntent(StrEnum):
    """Time Off module intents"""
    REQUEST_VACATION = "request_vacation"
    CHECK_VACATION_BALANCE = "check_vacation_balance"


class PeopleOpsIntent(StrEnum):
    """People Ops module intents"""
    ONBOARDING = "onboarding"
    SCHEDULE_MEETING = "schedule_meeting"  # Legacy - redirects to Scheduling module
    WELCOME_CHECKLIST = "welcome_checklist"
    OFFBOARDING = "offboarding"


class KnowledgeBaseIntent(StrEnum):
    """Knowledge Base module intents"""
    ASK_QUESTION = "ask_question"


class ServiceDeskIntent(StrEnum):
    """Service Desk module intents"""
    REQUEST_ACCESS = "request_access"
    REQUEST_EQUIPMENT = "request_equipment"


class GeneralIntent(StrEnum):
    """General intents (not tied to any specific module)"""
    CHAT = "chat"
    UNKNOWN = "unknown"  # When LLM cannot determine the intent


# ============================================================================
# Type Alias for Type Hinting
# ============================================================================

# This is not logic, just type hinting, so it can live here
AnyIntent = Union[
    SchedulingIntent,
    TimeOffIntent,
    PeopleOpsIntent,
    KnowledgeBaseIntent,
    ServiceDeskIntent,
    GeneralIntent
]

# Alias for backward compatibility
BotIntent = AnyIntent

