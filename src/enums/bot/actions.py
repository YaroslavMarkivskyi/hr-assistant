"""
Action types that can be executed through Adaptive Cards or commands

This file contains only action enum definitions.
Actions are UI interactions (button clicks), separate from intents (NLP).
"""
from enum import StrEnum
from typing import List
from .modules import BotModule


class BotAction(StrEnum):
    """
    Action types that can be executed through Adaptive Cards or commands
    
    Actions are UI interactions (button clicks), separate from intents (NLP).
    Currently only Scheduling actions are implemented.
    """
    # Scheduling - Find Time
    SELECT_TIME_SLOT = "select_time_slot"  # Select a time slot from availability
    SHOW_MORE_SLOTS = "show_more_slots"  # Show more time options
    BOOK_SLOT = "book_slot"  # Book selected time slot
    
    # Scheduling - Booking
    CONFIRM_BOOKING = "confirm_booking"  # Confirm meeting booking
    ADD_EXTERNAL_GUEST = "add_external_guest"  # Add external guest by email
    ADD_GROUP = "add_group"  # Add Azure AD group
    
    # Scheduling - CRUD
    RESCHEDULE_MEETING = "reschedule_meeting"  # Reschedule existing meeting
    CANCEL_MEETING = "cancel_meeting_action"  # Cancel meeting (action from card)
    UPDATE_NOTIFICATION_PREFERENCE = "update_notification_preference"  # Who to notify on update
    
    # Scheduling - Workshop
    IGNORE_AVAILABILITY_TOGGLE = "ignore_availability_toggle"  # Toggle ignore availability for workshop
    CONFIRM_WORKSHOP = "confirm_workshop"  # Confirm workshop creation
    
    # Scheduling - Daily Briefing
    VIEW_CALENDAR_DETAILS = "view_calendar_details"  # View detailed calendar info
    
    def get_module(self) -> BotModule:
        """
        Returns the module this action belongs to.
        
        NOTE: This method is kept here for backward compatibility.
        For new code, use registry.get_module_for_action() instead.
        
        Currently all actions belong to SCHEDULING module.
        """
        # All current actions belong to SCHEDULING
        return BotModule.SCHEDULING
    
    @classmethod
    def get_actions_by_module(cls, module: BotModule) -> List['BotAction']:
        """
        Returns a list of actions for a specific module.
        
        NOTE: For new code, use registry.get_actions_by_module() instead.
        This method is kept for backward compatibility.
        """
        # Filter actions by module using get_module() method
        return [action for action in cls if action.get_module() == module]

