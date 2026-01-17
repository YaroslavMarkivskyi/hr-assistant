from typing import Union

from .scheduling import SchedulingAction
from .time_off import TimeOffAction
from .general import GeneralAction


BotAction = Union[
    SchedulingAction,
    GeneralAction,
    TimeOffAction
]

__all__ = (
    "SchedulingAction",
    "TimeOffAction",
    "GeneralAction",
    "BotAction",
)