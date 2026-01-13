"""
Registry: Mappings, validation, and helper functions

This is the "glue" that connects modules, intents, and actions.
All logic for routing and validation lives here to avoid circular imports.
"""
from typing import Dict, Type, List, Optional
from enum import StrEnum

# Import definitions (not logic) - safe from circular imports
from .modules import BotModule

from .intents import (
    SchedulingIntent,
    GeneralIntent,
    AnyIntent,
)

from .actions import (
    SchedulingAction,
    GeneralAction,
    AnyAction,
    BotAction, # Alias
)


# ============================================================================
# Intent Mappings (Auto-generated)
# ============================================================================

# Map: Module -> Intent Enum Class
MODULE_TO_INTENT_ENUM: Dict[BotModule, Type[StrEnum]] = {
    BotModule.SCHEDULING: SchedulingIntent,
    # GeneralIntent usually handles fallback/chitchat, often not mapped to a specific module 
    # or mapped to BotModule.GENERAL if you have one.
}

# Map: Intent String -> BotModule (O(1) lookup)
INTENT_TO_MODULE_MAP: Dict[str, BotModule] = {}

for module, enum_cls in MODULE_TO_INTENT_ENUM.items():
    for intent in enum_cls:
        if intent.value in INTENT_TO_MODULE_MAP:
            raise ValueError(
                f"DUPLICATE INTENT: '{intent.value}' defined in {INTENT_TO_MODULE_MAP[intent.value]} and {module}"
            )
        INTENT_TO_MODULE_MAP[intent.value] = module

# Aliases
INTENT_MODULE_MAP = INTENT_TO_MODULE_MAP
MODULE_INTENT_MAP = MODULE_TO_INTENT_ENUM


# ============================================================================
# Action Mappings (Auto-generated)
# ============================================================================

ACTION_CLASS_TO_MODULE: Dict[Type[StrEnum], BotModule] = {
    SchedulingAction: BotModule.SCHEDULING,
    GeneralAction: BotModule.GENERAL, 
}

# Map: Action String -> BotModule (O(1) lookup)
ACTION_TO_MODULE_MAP: Dict[str, BotModule] = {}

for enum_cls, module in ACTION_CLASS_TO_MODULE.items():
    for action in enum_cls:
        # Validation: Check for duplicates
        if action.value in ACTION_TO_MODULE_MAP:
            existing_module = ACTION_TO_MODULE_MAP[action.value]
            raise ValueError(
                f"DUPLICATE ACTION: '{action.value}' defined in {existing_module} and {module}"
            )
        ACTION_TO_MODULE_MAP[action.value] = module


# ============================================================================
# Helper Functions: Intents
# ============================================================================

def get_module_for_intent(intent_value: str) -> BotModule | None:
    return INTENT_TO_MODULE_MAP.get(intent_value)


def validate_intent(module: BotModule, intent_value: str) -> bool:
    enum_cls = MODULE_TO_INTENT_ENUM.get(module)
    if not enum_cls:
        return False
    return intent_value in enum_cls._value2member_map_


def get_intent_enum(intent_value: str) -> AnyIntent | None:
    # 1. Try module specific
    module = get_module_for_intent(intent_value)
    if module:
        enum_cls = MODULE_TO_INTENT_ENUM.get(module)
        if enum_cls:
            try:
                return enum_cls(intent_value)
            except ValueError:
                pass
    
    # 2. Try General
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
    Works with both 'str' and 'StrEnum' members.
    """
    return ACTION_TO_MODULE_MAP.get(action_value)


def get_actions_by_module(module: BotModule) -> List[BotAction]:
    """
    Returns a list of specific Action Enums for a module.
    """
    target_cls = None
    for cls, mod in ACTION_CLASS_TO_MODULE.items():
        if mod == module:
            target_cls = cls
            break
            
    if target_cls:
        return list(target_cls)
    return []

def get_action_enum(action_value: str) -> BotAction | None:
    """
    Converts raw action string to specific Enum instance (SchedulingAction, etc).
    Useful for type narrowing in controllers.
    """
    module = get_module_for_action(action_value)
    if not module:
        return None
        
    # Find the class belonging to this module
    for enum_cls, mod in ACTION_CLASS_TO_MODULE.items():
        if mod == module:
            try:
                return enum_cls(action_value)
            except ValueError:
                pass
                
    return None