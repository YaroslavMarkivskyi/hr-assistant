"""
Common handlers for general intents (chat, unknown, etc.)
"""
from microsoft.teams.apps import ActivityContext
from enums import BotCapability, BotModule
from resources import get_translation, get_module_name, get_capability_name
from utils.helpers import get_user_language


async def handle_unknown_intent(ctx: ActivityContext) -> None:
    """
    Handles unknown intent - shows help message
    
    Args:
        ctx: Activity context from Teams
    """
    language = get_user_language(ctx)
    message = get_translation("message.unknown_intent", language)
    await ctx.send(message)


async def handle_chat_intent(ctx: ActivityContext) -> None:
    """
    Handles chat intent - shows bot capabilities
    
    Args:
        ctx: Activity context from Teams
    """
    language = get_user_language(ctx)
    
    # Group capabilities by modules
    modules_info = {}
    for cap in BotCapability:
        module = cap.get_module()
        if module not in modules_info:
            modules_info[module] = []
        modules_info[module].append(cap)
    
    # Build message with localization
    message_parts = [get_translation("message.chat_greeting", language)]
    for module, capabilities in modules_info.items():
        module_name = get_module_name(module, language)
        message_parts.append(f"\n📦 **{module_name}:**")
        for cap in capabilities:
            cap_name = get_capability_name(cap, language)
            message_parts.append(f"  • {cap_name}")
    
    message_parts.append(get_translation("message.chat_footer", language))
    await ctx.send("\n".join(message_parts))

