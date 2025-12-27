"""
Bot modules - main functional blocks
"""
from enum import StrEnum
from typing import List


class BotModule(StrEnum):
    """
    Bot modules - main functional blocks of the bot
    """
    PEOPLE_OPS = "people_ops"
    TIME_OFF = "time_off"
    KNOWLEDGE_BASE = "knowledge_base"
    SERVICE_DESK = "service_desk"
    
    def get_submodules(self) -> List[str]:
        """Returns a list of submodules for this module"""
        submodules = {
            self.PEOPLE_OPS: ["onboarding", "scheduling", "welcome_checklist", "offboarding"],
            self.TIME_OFF: ["request_vacation", "approve_reject", "balance"],
            self.KNOWLEDGE_BASE: ["qa"],
            self.SERVICE_DESK: ["request_access", "request_equipment"]
        }
        return submodules.get(self, [])

