from typing import Dict, Type
from dataclasses import dataclass

from pydantic import BaseModel

from core.enums.prompts import PromptKeys
from core.enums.bot import BotIntent, SchedulingIntent

from schemas.ai.scheduling import ScheduleQueryEntities


@dataclass
class ExtractionConfig:
    schema: Type[BaseModel]
    prompt_key: PromptKeys

""" 
EXAMPLE:
EXTRACTOR_REGISTRY: Dict[BotIntent, ExtractionConfig] = {
    BotIntent.TIME_OFF_APPLY: ExtractionConfig(
        schema=TimeOffData,
        prompt_key=PromptKeys.TIME_OFF_EXTRACT
    ),
    BotIntent.SCHEDULING_BOOK: ExtractionConfig(
        schema=MeetingData,
        prompt_key=PromptKeys.SCHEDULING_EXTRACT
    ),
}
"""

EXTRACTOR_REGISTRY: Dict[BotIntent, ExtractionConfig] = {
    SchedulingIntent.FIND_TIME: ExtractionConfig(
        schema=ScheduleQueryEntities,
        prompt_key=PromptKeys.SCHEDULING_EXTRACT
    ),
}

__all__ = (
    "EXTRACTOR_REGISTRY",
)

