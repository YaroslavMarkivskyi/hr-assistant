"""
Bot enums package - Facade for easy imports

This package provides a clean, organized structure for bot enums.
Updated to support module-specific Actions (SchedulingAction, GeneralAction).
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
from .actions import (
    SchedulingAction,
    GeneralAction,
    AnyAction,
    BotAction, # Alias for AnyAction (backward compatibility)
)

# Import registry (mappings and helpers)
from .registry import (
    # Intent mappings
    MODULE_TO_INTENT_ENUM,
    MODULE_INTENT_MAP,
    INTENT_TO_MODULE_MAP,
    INTENT_MODULE_MAP,
    
    # Action mappings
    ACTION_CLASS_TO_MODULE,
    
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
    
    'SchedulingAction',
    'GeneralAction',
    'AnyAction',
    'BotAction',
    
    # Intent mappings
    'MODULE_TO_INTENT_ENUM',
    'MODULE_INTENT_MAP',
    'INTENT_TO_MODULE_MAP',
    'INTENT_MODULE_MAP',
    
    # Action mappings
    'ACTION_CLASS_TO_MODULE',
    
    # Helper functions: Intents
    'get_module_for_intent',
    'validate_intent',
    'get_intent_enum',
    
    # Helper functions: Actions
    'get_module_for_action',
    'get_actions_by_module',
]