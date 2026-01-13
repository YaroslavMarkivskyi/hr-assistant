"""
Action payload model for Adaptive Card button clicks.

This module defines a strict contract for button payloads coming from Teams.
It uses Pydantic for validation to avoid guessing payload structure
and to ensure the action is a valid BotAction.
"""
from __future__ import annotations
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from enums.bot import BotAction
from enums.bot.registry import get_action_enum



class ActionPayload(BaseModel):
    """
    Strict contract for button payloads.
    """

    action: BotAction = Field(
        ..., 
        description="Action to perform, must be valid BotAction enum value"
        )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional contextual data for the action (card-specific payload)",
    )

    @field_validator("action", mode="before")
    @classmethod
    def validate_action(cls, v: Any) -> BotAction:
        """
        Ensure the action is a valid BotAction.
        Converts string value to specific Enum member using registry lookup.
        """
        if hasattr(v, "value"):
            # Already an Enum member
            return v
        
        str_value = str(v)
        
        action_enum = get_action_enum(str_value)
        
        if action_enum is None:
            raise ValueError(f"Invalid action value: '{str_value}' is not registered in any module")
        
        return action_enum
