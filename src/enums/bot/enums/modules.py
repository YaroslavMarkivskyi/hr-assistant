"""
Bot modules - main functional blocks

This file contains only module definitions. It rarely changes.
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
    RECRUITMENT = "recruitment"
    SCHEDULING = "scheduling"
