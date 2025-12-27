"""
User intent types that the bot recognizes
"""
from enum import StrEnum
from .bot_module import BotModule


class BotIntent(StrEnum):
    """
    User intent types that the bot recognizes
    """
    # People Ops
    ONBOARDING = "onboarding"
    SCHEDULE_MEETING = "schedule_meeting"
    WELCOME_CHECKLIST = "welcome_checklist"
    OFFBOARDING = "offboarding"
    
    # Time Off
    REQUEST_VACATION = "request_vacation"
    CHECK_VACATION_BALANCE = "check_vacation_balance"
    
    # Knowledge Base
    ASK_QUESTION = "ask_question"
    
    # Service Desk
    REQUEST_ACCESS = "request_access"
    REQUEST_EQUIPMENT = "request_equipment"
    
    # General
    CHAT = "chat"
    
    # Unknown - when LLM cannot determine the intent
    UNKNOWN = "unknown"
    
    def get_module(self) -> BotModule | None:
        """Returns the module this intent belongs to, 
        or None if it doesn't belong to any module.
        """
        module_map = {
            # People Ops
            self.ONBOARDING: BotModule.PEOPLE_OPS,
            self.SCHEDULE_MEETING: BotModule.PEOPLE_OPS,
            self.WELCOME_CHECKLIST: BotModule.PEOPLE_OPS,
            self.OFFBOARDING: BotModule.PEOPLE_OPS,
            
            # Time Off
            self.REQUEST_VACATION: BotModule.TIME_OFF,
            self.CHECK_VACATION_BALANCE: BotModule.TIME_OFF,
            
            # Knowledge Base
            self.ASK_QUESTION: BotModule.KNOWLEDGE_BASE,
            
            # Service Desk
            self.REQUEST_ACCESS: BotModule.SERVICE_DESK,
            self.REQUEST_EQUIPMENT: BotModule.SERVICE_DESK,
            
            # General
            self.CHAT: None,  # Does not belong to any module
            self.UNKNOWN: None  # Unknown intent - does not belong to any module
        }
        return module_map.get(self)

