from enum import StrEnum


class BotRequestType(StrEnum):
    ACTION = "action"
    INTENT = "intent"
    
__all__ = (
    "BotRequestType",
)

