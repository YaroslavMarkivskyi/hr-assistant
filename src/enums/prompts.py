from enum import StrEnum

from .bot import BotModule


class PromptKeys(StrEnum):
    ROUTER = "router"
    
    # Scheduling module prompts
    SCHEDULING_EXTRACT = f"{BotModule.SCHEDULING}/extract"
    SCHEDULING_VIEW = f"{BotModule.SCHEDULING}/view"
    SCHEDULING_CANCEL = f"{BotModule.SCHEDULING}/cancel"
    SCHEDULING_UPDATE = f"{BotModule.SCHEDULING}/update"
    
    
__all__ = [
    "PromptKeys"
]

