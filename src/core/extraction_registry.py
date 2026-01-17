from typing import Dict, Type

from dataclasses import dataclass

from core.enums.prompts import PromptKeys
from pydantic import BaseModel

from core.enums.bot import BotIntent


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
    
}

__all__ = (
    "EXTRACTOR_REGISTRY",
)

