from enum import StrEnum

from .bot import BotModule


class PromptKeys(StrEnum):
    ROUTER = "router"
    
    # Scheduling module prompts
    SCHEDULING_EXTRACT = f"{BotModule.SCHEDULING}/extract"
    SCHEDULING_VIEW = f"{BotModule.SCHEDULING}/view"
    SCHEDULING_CANCEL = f"{BotModule.SCHEDULING}/cancel"
    SCHEDULING_UPDATE = f"{BotModule.SCHEDULING}/update"
    
    # Time Off module prompts
    TIMEOFF_EXTRACT = f"{BotModule.TIME_OFF}/extract"
    TIMEOFF_VIEW = f"{BotModule.TIME_OFF}/view"
    TIMEOFF_CANCEL = f"{BotModule.TIME_OFF}/cancel"
    TIMEOFF_REQUEST = f"{BotModule.TIME_OFF}/request"
    
    
__all__ = [
    "PromptKeys"
]

