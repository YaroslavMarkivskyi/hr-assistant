"""
Bot enums package - Facade for easy imports

This package provides a clean, organized structure for bot enums:
- modules.py: BotModule definitions
- intents.py: Intent enum definitions (SchedulingIntent, etc.)
- actions.py: Action enum definitions (BotAction)
- registry.py: Mappings, validation, and helper functions

Usage:
    from enums.bot import BotModule, SchedulingIntent, BotAction
    from enums.bot import get_intent_enum, get_module_for_intent
"""
# Import modules
from .modules import BotModule

# Import intents
from .intents import (
    SchedulingIntent,
    GeneralIntent,
    AnyIntent,
    BotIntent,  # Alias for AnyIntent (backward compatibility)
)

# Import actions
from .actions import BotAction

# Import registry (mappings and helpers)
from .registry import (
    # Intent mappings
    MODULE_TO_INTENT_ENUM,
    MODULE_INTENT_MAP,  # Alias for MODULE_TO_INTENT_ENUM
    INTENT_TO_MODULE_MAP,
    INTENT_MODULE_MAP,  # Alias for INTENT_TO_MODULE_MAP
    # Action mappings
    ACTION_TO_MODULE_MAP,
    # Helper functions: Intents
    get_module_for_intent,
    validate_intent,
    get_intent_enum,
    # Helper functions: Actions
    get_module_for_action,
    get_actions_by_module,
)

__all__ = [
    # Modules
    'BotModule',
    # Intents
    'SchedulingIntent',
    'GeneralIntent',
    'AnyIntent',
    'BotIntent',
    # Actions
    'BotAction',
    # Intent mappings
    'MODULE_TO_INTENT_ENUM',
    'MODULE_INTENT_MAP',
    'INTENT_TO_MODULE_MAP',
    'INTENT_MODULE_MAP',
    # Action mappings
    'ACTION_TO_MODULE_MAP',
    # Helper functions: Intents
    'get_module_for_intent',
    'validate_intent',
    'get_intent_enum',
    # Helper functions: Actions
    'get_module_for_action',
    'get_actions_by_module',
]
