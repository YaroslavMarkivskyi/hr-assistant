"""
Bot capabilities - what the bot can do

NOTE: BotCapability is used only for displaying bot capabilities in chat.
Consider removing it and using BotIntent instead, as it duplicates information.
"""
from enum import StrEnum
from .bot.modules import BotModule


class BotCapability(StrEnum):
    """
    Bot capabilities - detailed list of what the bot can do
    """
    # People Ops
    CREATE_USER = "create_user"
    SCHEDULE_MEETING = "schedule_meeting"
    WELCOME_CHECKLIST = "welcome_checklist"
    OFFBOARDING = "offboarding"
    
    # Time Off
    REQUEST_VACATION = "request_vacation"
    APPROVE_VACATION = "approve_vacation"
    CHECK_VACATION_BALANCE = "check_vacation_balance"
    
    # Knowledge Base
    ANSWER_QUESTION = "answer_question"
    
    # Service Desk
    REQUEST_ACCESS = "request_access"
    REQUEST_EQUIPMENT = "request_equipment"
    
    def get_module(self) -> BotModule:
        """Returns the module this capability belongs to"""
        module_map = {
            # People Ops
            self.CREATE_USER: BotModule.PEOPLE_OPS,
            self.SCHEDULE_MEETING: BotModule.PEOPLE_OPS,
            self.WELCOME_CHECKLIST: BotModule.PEOPLE_OPS,
            self.OFFBOARDING: BotModule.PEOPLE_OPS,
            
            # Time Off
            self.REQUEST_VACATION: BotModule.TIME_OFF,
            self.APPROVE_VACATION: BotModule.TIME_OFF,
            self.CHECK_VACATION_BALANCE: BotModule.TIME_OFF,
            
            # Knowledge Base
            self.ANSWER_QUESTION: BotModule.KNOWLEDGE_BASE,
            
            # Service Desk
            self.REQUEST_ACCESS: BotModule.SERVICE_DESK,
            self.REQUEST_EQUIPMENT: BotModule.SERVICE_DESK
        }
        return module_map.get(self, BotModule.PEOPLE_OPS)

