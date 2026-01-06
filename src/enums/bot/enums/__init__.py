"""
Bot Enums Package

Facade that exports all enums and registry functions for convenient imports.

Usage:
    from enums.bot.enums import BotModule, SchedulingIntent, BotAction, get_intent_enum
"""
# Import definitions
from .modules import BotModule
from .intents import (
    SchedulingIntent,
    TimeOffIntent,
    PeopleOpsIntent,
    KnowledgeBaseIntent,
    ServiceDeskIntent,
    GeneralIntent,
    AnyIntent,
    BotIntent,  # Alias for AnyIntent (backward compatibility)
)
from .actions import BotAction

# Import registry (mappings and helpers)
from .registry import (
    # Mappings
    MODULE_TO_INTENT_ENUM,
    MODULE_INTENT_MAP,  # Alias for MODULE_TO_INTENT_ENUM
    INTENT_TO_MODULE_MAP,
    INTENT_MODULE_MAP,  # Alias for INTENT_TO_MODULE_MAP
    ACTION_TO_MODULE_MAP,
    # Helper functions
    get_module_for_intent,
    validate_intent,
    get_intent_enum,
    get_module_for_action,
)

__all__ = [
    # Modules
    'BotModule',
    # Intents
    'SchedulingIntent',
    'TimeOffIntent',
    'PeopleOpsIntent',
    'KnowledgeBaseIntent',
    'ServiceDeskIntent',
    'GeneralIntent',
    'AnyIntent',
    'BotIntent',  # Backward compatibility
    # Actions
    'BotAction',
    # Mappings
    'MODULE_TO_INTENT_ENUM',
    'MODULE_INTENT_MAP',
    'INTENT_TO_MODULE_MAP',
    'INTENT_MODULE_MAP',
    'ACTION_TO_MODULE_MAP',
    # Helper functions
    'get_module_for_intent',
    'validate_intent',
    'get_intent_enum',
    'get_module_for_action',
]

