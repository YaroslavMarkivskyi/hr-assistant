"""
AI Response Model.

Defines the strict contract for data returned by the AI Service.
Uses Pydantic to validate structure and prevent logical inconsistencies
between predicted module and intent.
"""
from __future__ import annotations

from typing import Dict, Any, Optional, Literal

from pydantic import BaseModel, Field, model_validator

from core.enums.bot import BotModule, GeneralIntent, get_module_for_intent


class AIResponse(BaseModel):
    """
    Standardized structured response from the AI.

    Used to route user requests to the correct feature module.
    """

    # 1. Module (e.g. 'scheduling', 'time_off')
    # Optional because some intents (chat/unknown) are not tied to modules.
    # When omitted, we will infer it from the intent where possible.
    module: Optional[BotModule] = Field(
        default=None,
        description="The domain module responsible for handling this request (if applicable).",
    )

    # 2. Intent (e.g. 'book_meeting')
    # We accept a string but validate its logic below
    intent: str = Field(
        ...,
        description="The specific action identifier (e.g., 'book_meeting').",
    )

    # 3. Entities (parameters)
    # Free-form dictionary; structure depends on the intent
    entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted parameters (e.g. {'date': 'tomorrow', 'person': 'Oleg'}).",
    )

    # 4. Confidence
    confidence: float = Field(
        ...,
        description="Confidence score between 0.0 and 1.0.",
    )

    # 5. Explanation (reasoning / chain-of-thought summary)
    # Useful for debugging why a particular intent was chosen
    reasoning: Optional[str] = Field(
        None,
        description="Short explanation of why this intent was chosen.",
    )

    # 6. Language detection
    # LLM determines the language of the user's message (en/uk)
    # This is more reliable than regex-based detection as LLM understands:
    # - Context (e.g., "meeting" is English even if written in Cyrillic "мітинг")
    # - Transliteration (e.g., "pryvit" -> Ukrainian)
    # - Mixed text
    language: Literal["en", "uk"] = Field(
        default="en",
        description="Detected language of the user's message. Use 'en' for English, 'uk' for Ukrainian. "
                   "Consider context, transliteration, and mixed text when determining language.",
    )

    # ======================================================================
    # ANTI-HALLUCINATION VALIDATOR
    # ======================================================================
    @model_validator(mode="after")
    def validate_intent_consistency(self) -> "AIResponse":
        """
        Ensures that the predicted 'intent' actually belongs to the predicted 'module'.

        Example: prevents module='time_off' with intent='book_meeting'.
        """
        expected_module = get_module_for_intent(self.intent)

        # 1. Intent completely unknown to the system -> hallucination
        if expected_module is None:
            # General intents like "chat" / "unknown" are not mapped to modules
            # and are handled separately via GeneralIntent, so they are allowed.
            # Use Enum values instead of hardcoded strings for maintainability
            general_intent_values = {GeneralIntent.UNKNOWN.value, GeneralIntent.CHAT.value}
            if self.intent in general_intent_values:
                # CRITICAL: Force module to None for general intents to prevent routing errors.
                # Even if LLM "hallucinated" and returned a module (e.g., module="scheduling" with intent="chat"),
                # we must override it to None to ensure the request goes to GeneralController.
                self.module = None
                return self

            raise ValueError(f"CRITICAL: AI predicted unknown intent '{self.intent}'")

        # 2. If module was not provided, infer it from the registry
        if self.module is None:
            self.module = expected_module
            return self

        # 3. If module was provided, ensure it matches registry
        if expected_module != self.module:
            raise ValueError(
                f"Consistency Error: Intent '{self.intent}' belongs to '{expected_module}', "
                f"but AI predicted module '{self.module}'."
            )

        return self


__all__ = (
    "AIResponse",
)

