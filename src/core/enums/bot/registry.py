from functools import cache
from typing import Dict, Optional, Tuple
from enum import StrEnum

from .bot_module import BotModule

from .actions import (
    SchedulingAction,
    TimeOffAction,
    GeneralAction,
)

from .intents import (
    SchedulingIntent,
    TimeOffIntent,
    GeneralIntent,
)

_MAPS = {
    "action": {
        SchedulingAction:   BotModule.SCHEDULING,
        TimeOffAction:      BotModule.TIME_OFF,
        GeneralAction:      BotModule.GENERAL,
    },
    "intent": {
        SchedulingIntent:   BotModule.SCHEDULING,
        TimeOffIntent:      BotModule.TIME_OFF,
        GeneralIntent:      BotModule.GENERAL,
    }
}


@cache
def _get_index(registry_type: str) -> Tuple[Dict[str, BotModule], Dict[str, StrEnum]]:
    mapping = _MAPS[registry_type]
    return (
        {m.value: mod for cls, mod in mapping.items() for m in cls},
        {m.value: m for cls in mapping for m in cls}
    )


def get_module_for_action(val: str) -> Optional[BotModule]:
    return _get_index("action")[0].get(val)

def get_action_enum_instance(val: str) -> Optional[StrEnum]:
    return _get_index("action")[1].get(val)

def get_module_for_intent(val: str) -> Optional[BotModule]:
    return _get_index("intent")[0].get(val)

def get_intent_enum_instance(val: str) -> Optional[StrEnum]:
    return _get_index("intent")[1].get(val)


__all__ = (
    "get_module_for_action",
    "get_action_enum_instance",
    "get_module_for_intent",
    "get_intent_enum_instance",
)

