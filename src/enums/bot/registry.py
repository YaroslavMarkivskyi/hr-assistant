"""
Registry: Mappings, validation, and helper functions

This is the "glue" that connects modules, intents, and actions.
All logic for routing and validation lives here to avoid circular imports.
"""
from typing import Dict, Type, List
from enum import StrEnum

# Import definitions (not logic) - safe from circular imports
from .modules import BotModule
from .intents import (
    SchedulingIntent,
    GeneralIntent,
    AnyIntent,
)
from .actions import BotAction


# ============================================================================
# Intent Mappings (Auto-generated)
# ============================================================================

# Map: Module -> Intent Enum Class
MODULE_TO_INTENT_ENUM: Dict[BotModule, Type[StrEnum]] = {
    BotModule.SCHEDULING: SchedulingIntent,
    # NOTE: GeneralIntent (CHAT, UNKNOWN) doesn't belong to any module
}

# Map: Intent String -> BotModule (O(1) lookup)
# Dynamically generated to avoid duplication
INTENT_TO_MODULE_MAP: Dict[str, BotModule] = {}

for module, enum_cls in MODULE_TO_INTENT_ENUM.items():
    for intent in enum_cls:
        # Validation: Check for duplicate intent values
        if intent.value in INTENT_TO_MODULE_MAP:
            raise ValueError(
                f"DUPLICATE INTENT DETECTED: '{intent.value}' is defined in multiple modules! "
                f"First in {INTENT_TO_MODULE_MAP[intent.value]}, now in {module}"
            )
        INTENT_TO_MODULE_MAP[intent.value] = module

# Aliases for backward compatibility
INTENT_MODULE_MAP = INTENT_TO_MODULE_MAP
MODULE_INTENT_MAP = MODULE_TO_INTENT_ENUM


# ============================================================================
# Action Mappings (Auto-generated)
# ============================================================================

# Map: Action String -> BotModule (O(1) lookup)
# Dynamically generated from BotAction.get_module() method
ACTION_TO_MODULE_MAP: Dict[str, BotModule] = {}

# Build action-to-module mapping
# All current actions belong to SCHEDULING module
_action_module_map = {
    # Scheduling
    BotAction.SELECT_TIME_SLOT.value: BotModule.SCHEDULING,
    BotAction.SHOW_MORE_SLOTS.value: BotModule.SCHEDULING,
    BotAction.BOOK_SLOT.value: BotModule.SCHEDULING,
    BotAction.CONFIRM_BOOKING.value: BotModule.SCHEDULING,
    BotAction.ADD_EXTERNAL_GUEST.value: BotModule.SCHEDULING,
    BotAction.ADD_GROUP.value: BotModule.SCHEDULING,
    BotAction.RESCHEDULE_MEETING.value: BotModule.SCHEDULING,
    BotAction.CANCEL_MEETING.value: BotModule.SCHEDULING,
    BotAction.UPDATE_NOTIFICATION_PREFERENCE.value: BotModule.SCHEDULING,
    BotAction.IGNORE_AVAILABILITY_TOGGLE.value: BotModule.SCHEDULING,
    BotAction.CONFIRM_WORKSHOP.value: BotModule.SCHEDULING,
    BotAction.VIEW_CALENDAR_DETAILS.value: BotModule.SCHEDULING,
}

ACTION_TO_MODULE_MAP.update(_action_module_map)


# ============================================================================
# Helper Functions: Intents
# ============================================================================

def get_module_for_intent(intent_value: str) -> BotModule | None:
    """
    Fast O(1) lookup to find which module owns an intent.
    
    Args:
        intent_value: Intent string value (e.g., "find_time", "onboarding")
        
    Returns:
        BotModule if found, None otherwise (e.g., for GeneralIntent)
    """
    return INTENT_TO_MODULE_MAP.get(intent_value)


def validate_intent(module: BotModule, intent_value: str) -> bool:
    """
    Checks if a string intent belongs to the specified module.
    
    Args:
        module: BotModule to check against
        intent_value: Intent string value
        
    Returns:
        True if intent belongs to module, False otherwise
    """
    enum_cls = MODULE_TO_INTENT_ENUM.get(module)
    if not enum_cls:
        return False
    # Check if value exists in this Enum
    return intent_value in enum_cls._value2member_map_


def get_intent_enum(intent_value: str) -> AnyIntent | None:
    """
    Converts intent string to appropriate enum instance.
    
    Args:
        intent_value: Intent string value
        
    Returns:
        Enum instance (SchedulingIntent, TimeOffIntent, GeneralIntent, etc.) or None if invalid
    """
    # First, try to find module-specific intent
    module = get_module_for_intent(intent_value)
    if module:
        enum_cls = MODULE_TO_INTENT_ENUM.get(module)
        if enum_cls:
            try:
                return enum_cls(intent_value)
            except ValueError:
                pass
    
    # If not found in modules, try GeneralIntent (CHAT, UNKNOWN)
    try:
        return GeneralIntent(intent_value)
    except ValueError:
        return None


# ============================================================================
# Helper Functions: Actions
# ============================================================================

def get_module_for_action(action_value: str) -> BotModule | None:
    """
    Fast O(1) lookup to find which module owns an action.
    
    Args:
        action_value: Action string value (e.g., "confirm_booking", "approve_vacation")
        
    Returns:
        BotModule if found, None otherwise
    """
    return ACTION_TO_MODULE_MAP.get(action_value)


def get_actions_by_module(module: BotModule) -> List[BotAction]:
    """
    Returns a list of actions for a specific module.
    
    Args:
        module: BotModule to get actions for
        
    Returns:
        List of BotAction instances for the module
    """
    return [
        BotAction(action_value)
        for action_value, action_module in ACTION_TO_MODULE_MAP.items()
        if action_module == module
    ]

