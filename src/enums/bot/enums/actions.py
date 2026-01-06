"""
Action types that can be executed through Adaptive Cards or commands

This file contains only action enum definitions.
Actions are UI-related (button clicks), while Intents are NLP-related (user messages).
"""
from enum import StrEnum
from typing import List
from .modules import BotModule


class BotAction(StrEnum):
    """
    Action types that can be executed through Adaptive Cards or commands
    
    Actions are triggered by button clicks in Adaptive Cards, not by user text messages.
    """
    # People Ops - Onboarding
    CREATE_USER = "create_user"
    REJECT_CANDIDATE = "reject_candidate"
    
    # People Ops - Calendar
    SELECT_USER = "select_user"
    CONFIRM_MEETING = "confirm_meeting"
    REGENERATE_TIME = "regenerate_time"
    
    # People Ops - Welcome Checklist
    COMPLETE_CHECKLIST_ITEM = "complete_checklist_item"
    VIEW_CHECKLIST_PROGRESS = "view_checklist_progress"
    
    # People Ops - Offboarding
    CONFIRM_OFFBOARDING = "confirm_offboarding"
    CANCEL_OFFBOARDING = "cancel_offboarding"
    
    # Time Off
    APPROVE_VACATION = "approve_vacation"
    REJECT_VACATION = "reject_vacation"
    
    # Service Desk
    APPROVE_ACCESS_REQUEST = "approve_access_request"
    REJECT_ACCESS_REQUEST = "reject_access_request"
    APPROVE_EQUIPMENT_REQUEST = "approve_equipment_request"
    REJECT_EQUIPMENT_REQUEST = "reject_equipment_request"
    
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
        
        NOTE: Use get_module_for_action() from registry.py for better performance.
        This method is kept for backward compatibility.
        """
        # Lazy import to avoid circular dependency
        # registry.py imports BotAction, so we can't import it at module level
        from .registry import get_module_for_action
        return get_module_for_action(self.value) or BotModule.PEOPLE_OPS
    
    @classmethod
    def get_onboarding_actions(cls):
        """Returns a list of actions related to onboarding"""
        return [cls.CREATE_USER, cls.REJECT_CANDIDATE]
    
    @classmethod
    def get_calendar_actions(cls):
        """Returns a list of actions related to calendar"""
        return [cls.SELECT_USER, cls.CONFIRM_MEETING, cls.REGENERATE_TIME]
    
    @classmethod
    def get_actions_by_module(cls, module: BotModule) -> List['BotAction']:
        """Returns a list of actions for a specific module"""
        from .registry import get_module_for_action
        return [action for action in cls if get_module_for_action(action.value) == module]

