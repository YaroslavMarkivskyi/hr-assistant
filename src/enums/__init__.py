"""
Enums for defining bot capabilities and actions

Usage:
    # Import bot module (recommended)
    from enums import bot
    module = bot.BotModule.SCHEDULING
    intent = bot.SchedulingIntent.FIND_TIME
    action = bot.BotAction.CONFIRM_BOOKING
    
    # Or import directly from submodule
    from enums.bot import BotModule, SchedulingIntent, BotAction
"""
# Import bot as a module (not re-exporting individual items)
from . import bot
from .bot_capability import BotCapability
from .languages import Language
from .translation_key import TranslationKey

__all__ = [
    'bot',  # Main bot module (contains BotModule, BotIntent, BotAction, etc.)
    'BotCapability',
    'Language',
    'TranslationKey',
]

