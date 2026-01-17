from enum import StrEnum


class BotModule(StrEnum):
    SCHEDULING = "scheduling"
    GENERAL = "general"
    TIME_OFF = "time_off"

__all__ = ("BotModule",)

