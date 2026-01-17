from typing import Union

from .scheduling import SchedulingIntent
from .time_off import TimeOffIntent
from .general import GeneralIntent

BotIntent = Union[
    SchedulingIntent,
    GeneralIntent,
    TimeOffIntent
]

__all__ = (
    "SchedulingIntent",
    "TimeOffIntent",
    "GeneralIntent",
    "BotIntent",
)

