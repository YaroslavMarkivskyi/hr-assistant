"""
Bot Actions (Button Payloads)

This file contains definitions for button actions used in Adaptive Cards.
Actions are organized by modules for better structure and strict typing.
"""
from enum import StrEnum
from typing import Union, Dict

# ============================================================================
# Module-Specific Actions
# ============================================================================

class SchedulingAction(StrEnum):
    """Actions related to Scheduling Module"""
    
    # Find Time Flow
    SELECT_TIME_SLOT = "select_time_slot"      # User clicked on a specific slot
    SHOW_MORE_SLOTS = "show_more_slots"        # "Show more" button
    BOOK_SLOT = "book_slot"                    # Final booking button inside a slot
    
    # Booking Flow
    CONFIRM_BOOKING = "confirm_booking"        # Confirm details before final submit
    ADD_EXTERNAL_GUEST = "add_external_guest"  # Add email of non-org user
    ADD_GROUP = "add_group"                    # Add distribution list
    
    # CRUD Operations
    RESCHEDULE_MEETING = "reschedule_meeting"
    CANCEL_MEETING = "cancel_meeting"
    UPDATE_NOTIFICATION_PREFERENCE = "update_notification_preference"
    
    # Workshops
    IGNORE_AVAILABILITY_TOGGLE = "ignore_availability_toggle" # For "broadcast" events
    CONFIRM_WORKSHOP = "confirm_workshop"
    
    # Briefing / Views
    VIEW_CALENDAR_DETAILS = "view_calendar_details"


class GeneralAction(StrEnum):
    """General actions (Navigation, Help, Settings)"""
    OPEN_MAIN_MENU = "open_main_menu"
    GO_BACK = "go_back"
    CANCEL_OPERATION = "cancel_operation"
    Provide_Feedback = "provide_feedback"


class TimeOffAction(StrEnum):
    """Actions related to Time Off Module"""
    SUBMIT_REQUEST = "submit_timeoff_request"
    CANCEL_MY_REQUEST = "cancel_my_timeoff_request"


# ============================================================================
# Type Alias for Type Hinting
# ============================================================================

# Union type for all actions (use this in Dispatcher and ActionPayload)
AnyAction = Union[
    SchedulingAction,
    GeneralAction,
    TimeOffAction
]

# Alias for backward compatibility if needed
BotAction = AnyAction