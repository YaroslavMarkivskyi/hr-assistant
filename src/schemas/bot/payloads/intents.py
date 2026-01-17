"""
Intent payload schema definitions for bot routing.
"""
from __future__ import annotations
from typing import Any, Optional, Literal

from pydantic import BaseModel, Field, field_validator

from core.enums.bot import BotIntent, get_intent_enum_instance


class IntentPayload(BaseModel):
    """
    Strict contract for intent payloads.
    """

    intent: BotIntent = Field(
        ..., 
        description="Specific intent within the chosen module"
        )
    confidence: float = Field(
        ..., 
        description="Confidence score of the intent classification (0.0 to 1.0)"
        )
    language: Optional[Literal["en", "uk"]] = Field(
        None,
        description="Detected language of the user message"
    )
    original_text: str = Field(
        ...,
        description="Original user message text that led to this intent"
    )
    entities: Optional[dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional extracted entities relevant to the intent"
    )
    
    @field_validator("intent", mode="before")
    @classmethod
    def validate_intent(cls, value: Any) -> BotIntent:   
        if hasattr(value, "value"): return value
        
        intent_enum = get_intent_enum_instance(str(value))
        
        if intent_enum is None:
            raise ValueError(
                f"Intent value '{value}' is not registered in any module. "
                "Please add it to INTENT_MAP in core/enums/bot/registry.py."
                )
        return intent_enum
    

__all__ = (
    "IntentPayload",
)

