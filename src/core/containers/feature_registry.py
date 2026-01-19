from typing import Dict

from core.enums.bot import BotModule
from core.base import BaseModule

from features.scheduling import SchedulingModule
from features.time_off import TimeOffModule
from features.general import GeneralModule

from core.config import Config


def initialize_features(config: Config) -> Dict[BotModule, BaseModule]:
    """
    Initialize and return a registry of feature modules.
    """
    feature_registry: Dict[BotModule, BaseModule] = {
        BotModule.SCHEDULING: SchedulingModule(),
        BotModule.TIME_OFF: TimeOffModule(),
        BotModule.GENERAL: GeneralModule(),
    }
    
    return feature_registry


__all__ = (
    "initialize_features",
)

