"""
Action types that can be executed through Adaptive Cards or commands
"""
from enum import StrEnum
from typing import List
from .bot import BotModule


class BotAction(StrEnum):
    """
    Action types that can be executed through Adaptive Cards or commands
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
        """Returns the module this action belongs to"""
        module_map = {
            # People Ops
            self.CREATE_USER: BotModule.PEOPLE_OPS,
            self.REJECT_CANDIDATE: BotModule.PEOPLE_OPS,
            self.SELECT_USER: BotModule.PEOPLE_OPS,
            self.CONFIRM_MEETING: BotModule.PEOPLE_OPS,
            self.REGENERATE_TIME: BotModule.PEOPLE_OPS,
            self.COMPLETE_CHECKLIST_ITEM: BotModule.PEOPLE_OPS,
            self.VIEW_CHECKLIST_PROGRESS: BotModule.PEOPLE_OPS,
            self.CONFIRM_OFFBOARDING: BotModule.PEOPLE_OPS,
            self.CANCEL_OFFBOARDING: BotModule.PEOPLE_OPS,
            
            # Time Off
            self.APPROVE_VACATION: BotModule.TIME_OFF,
            self.REJECT_VACATION: BotModule.TIME_OFF,
            
            # Service Desk
            self.APPROVE_ACCESS_REQUEST: BotModule.SERVICE_DESK,
            self.REJECT_ACCESS_REQUEST: BotModule.SERVICE_DESK,
            self.APPROVE_EQUIPMENT_REQUEST: BotModule.SERVICE_DESK,
            self.REJECT_EQUIPMENT_REQUEST: BotModule.SERVICE_DESK,
            
            # Scheduling
            self.SELECT_TIME_SLOT: BotModule.SCHEDULING,
            self.SHOW_MORE_SLOTS: BotModule.SCHEDULING,
            self.BOOK_SLOT: BotModule.SCHEDULING,
            self.CONFIRM_BOOKING: BotModule.SCHEDULING,
            self.ADD_EXTERNAL_GUEST: BotModule.SCHEDULING,
            self.ADD_GROUP: BotModule.SCHEDULING,
            self.RESCHEDULE_MEETING: BotModule.SCHEDULING,
            self.CANCEL_MEETING: BotModule.SCHEDULING,
            self.UPDATE_NOTIFICATION_PREFERENCE: BotModule.SCHEDULING,
            self.IGNORE_AVAILABILITY_TOGGLE: BotModule.SCHEDULING,
            self.CONFIRM_WORKSHOP: BotModule.SCHEDULING,
            self.VIEW_CALENDAR_DETAILS: BotModule.SCHEDULING
        }
        return module_map.get(self, BotModule.PEOPLE_OPS)
    
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
        return [action for action in cls if action.get_module() == module]

