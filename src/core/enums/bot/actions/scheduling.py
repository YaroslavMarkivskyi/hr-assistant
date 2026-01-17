from enum import StrEnum


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
    

__all__ = ("SchedulingAction",)

