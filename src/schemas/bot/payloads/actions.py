"""
Action payload model for Adaptive Card button clicks.
"""
from __future__ import annotations
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from core.enums.bot import BotAction, get_action_enum_instance


class ActionPayload(BaseModel):
    """
    Strict contract for button payloads.
    """
    action: BotAction = Field(
        ..., 
        description="Action to perform, must be valid BotAction enum value"
        )
    # TODO: Change Any to Other strict type if needed
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional contextual data for the action (card-specific payload)",
    )

    @field_validator("action", mode="before")
    @classmethod
    def validate_action(cls, value: Any) -> BotAction:
        """
        Ensure the action is a valid BotAction.
        Converts string value to specific Enum member using registry lookup.
        """
        if hasattr(value, "value"): return value
        action_enum = get_action_enum_instance(str(value))
        
        if action_enum is None:
            raise ValueError(
                f"Action value '{value}' is not registered in any module. "
                "Please add it to ACTION_MAP in core/enums/bot/registry.py."
                )
        
        return action_enum


__all__ = (
    "ActionPayload",
)

