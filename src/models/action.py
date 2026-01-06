"""
Action payload model for Adaptive Card button clicks.

This module defines a strict contract for button payloads coming from Teams.
It uses Pydantic for validation to avoid guessing payload structure
and to ensure the action is a valid BotAction.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator

from enums.bot import BotAction


class ActionPayload(BaseModel):
    """
    Strict contract for button payloads.

    Expected schema (example):
    {
        "action": "select_time_slot",
        "context": {
            "slot_id": "123",
            "date": "2024-01-01"
        }
    }

    Fields:
    - action: must be a valid BotAction value
    - context: optional dictionary with arbitrary extra data
    """

    action: BotAction = Field(..., description="Action to perform, must be valid BotAction enum value")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional contextual data for the action (card-specific payload)",
    )

    @validator("action", pre=True)
    def validate_action(cls, v: Any) -> BotAction:
        """
        Ensure the action is a valid BotAction.

        Accepts either a BotAction instance or its string value.
        """
        if isinstance(v, BotAction):
            return v
        try:
            return BotAction(str(v))
        except ValueError as exc:
            # Re-raise as ValueError so router can distinguish validation errors
            raise ValueError(f"Invalid action value: {v}") from exc


