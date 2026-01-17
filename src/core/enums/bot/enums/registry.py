"""
Registry: Mappings, validation, and helper functions

This is the "glue" that connects modules, intents, and actions.
All logic lives here to avoid circular imports and duplication.
"""
from typing import Dict, Type
from enum import StrEnum

# Import definitions (not logic)
from .modules import BotModule
from .intents import (
    SchedulingIntent,
    TimeOffIntent,
    PeopleOpsIntent,
    KnowledgeBaseIntent,
    ServiceDeskIntent,
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
    BotModule.TIME_OFF: TimeOffIntent,
    BotModule.PEOPLE_OPS: PeopleOpsIntent,
    BotModule.KNOWLEDGE_BASE: KnowledgeBaseIntent,
    BotModule.SERVICE_DESK: ServiceDeskIntent,
    # NOTE: GeneralIntent (CHAT, UNKNOWN) doesn't belong to any module
}

# Map: Intent String -> BotModule (O(1) lookup)
# Auto-generated from module intents
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
# Auto-generated from BotAction enum
ACTION_TO_MODULE_MAP: Dict[str, BotModule] = {
    # People Ops
    BotAction.CREATE_USER.value: BotModule.PEOPLE_OPS,
    BotAction.REJECT_CANDIDATE.value: BotModule.PEOPLE_OPS,
    BotAction.SELECT_USER.value: BotModule.PEOPLE_OPS,
    BotAction.CONFIRM_MEETING.value: BotModule.PEOPLE_OPS,
    BotAction.REGENERATE_TIME.value: BotModule.PEOPLE_OPS,
    BotAction.COMPLETE_CHECKLIST_ITEM.value: BotModule.PEOPLE_OPS,
    BotAction.VIEW_CHECKLIST_PROGRESS.value: BotModule.PEOPLE_OPS,
    BotAction.CONFIRM_OFFBOARDING.value: BotModule.PEOPLE_OPS,
    BotAction.CANCEL_OFFBOARDING.value: BotModule.PEOPLE_OPS,
    # Time Off
    BotAction.APPROVE_VACATION.value: BotModule.TIME_OFF,
    BotAction.REJECT_VACATION.value: BotModule.TIME_OFF,
    # Service Desk
    BotAction.APPROVE_ACCESS_REQUEST.value: BotModule.SERVICE_DESK,
    BotAction.REJECT_ACCESS_REQUEST.value: BotModule.SERVICE_DESK,
    BotAction.APPROVE_EQUIPMENT_REQUEST.value: BotModule.SERVICE_DESK,
    BotAction.REJECT_EQUIPMENT_REQUEST.value: BotModule.SERVICE_DESK,
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


# ============================================================================
# Helper Functions
# ============================================================================

def get_module_for_intent(intent_value: str) -> BotModule | None:
    """
    Fast O(1) lookup to find which module owns an intent.
    
    Args:
        intent_value: Intent string value (e.g., "find_time", "onboarding")
        
    Returns:
        BotModule if found, None otherwise
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


def get_module_for_action(action_value: str) -> BotModule | None:
    """
    Fast O(1) lookup to find which module owns an action.
    
    Args:
        action_value: Action string value (e.g., "confirm_booking", "approve_vacation")
        
    Returns:
        BotModule if found, None otherwise
    """
    return ACTION_TO_MODULE_MAP.get(action_value)

