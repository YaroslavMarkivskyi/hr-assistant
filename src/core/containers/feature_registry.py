from __future__ import annotations
from typing import Dict, TYPE_CHECKING

from core.enums.bot import BotModule
from core.base import BaseModule

from features.scheduling import SchedulingModule
from features.time_off import TimeOffModule
from features.general import GeneralModule


if TYPE_CHECKING:
    from core.containers.service_container import ServiceContainer


def initialize_features(container: ServiceContainer) -> Dict[BotModule, BaseModule]:
    """
    Initialize and return a registry of feature modules.
    """
    feature_registry: Dict[BotModule, BaseModule] = {
        BotModule.SCHEDULING: SchedulingModule(container=container),
        # BotModule.TIME_OFF: TimeOffModule(container=container),
        # BotModule.GENERAL: GeneralModule(container=container),
    }
    
    return feature_registry


__all__ = (
    "initialize_features",
)

