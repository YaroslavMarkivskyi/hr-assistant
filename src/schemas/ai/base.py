from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from enums.bot import BotModule, BotIntent


class UserIntent(BaseModel):
    """User intent extracted from AI response"""
    module: BotModule = Field(
        ...,
        description="The logical module to route the request to. Choose based on user intent."
    )
    intent: BotIntent = Field(
        ...,
        description="The specific intent of the user within the chosen module."
    )
    confidence: float = Field(
        description="Confidence score of the intent classification (0.0 to 1.0)."
    )
    language: Optional[Literal["en", "uk"]] = Field(
        None,
        description="Detected language of the user message."
    )
    
    
__all__ = [
    "UserIntent"
    ]

