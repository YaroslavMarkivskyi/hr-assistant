"""
Resources package for translations and localization
"""
from .translations import (
    get_translation, 
    get_module_name, 
    get_capability_name, 
    get_intent_name, 
    get_action_name
)

__all__ = [
    'get_translation', 
    'get_module_name', 
    'get_capability_name', 
    'get_intent_name', 
    'get_action_name'
]

