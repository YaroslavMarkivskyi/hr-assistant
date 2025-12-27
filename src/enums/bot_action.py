"""
Action types that can be executed through Adaptive Cards or commands
"""
from enum import StrEnum
from typing import List
from .bot_module import BotModule


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
            self.REJECT_EQUIPMENT_REQUEST: BotModule.SERVICE_DESK
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

