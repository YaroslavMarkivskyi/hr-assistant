"""
General handlers for common intents (chat, unknown, etc.)
"""
from typing import Dict, Any

from bot.activity_context_wrapper import ActivityContextWrapper
from enums.bot import AnyIntent
from enums.translation_key import TranslationKey
from resources import get_translation
from utils.helpers import get_user_language
from container import ServiceContainer
from models.ai import AIResponse


async def handle_unknown_intent(
    ctx: ActivityContextWrapper,
    intent: str,  # pylint: disable=unused-argument
    ai_response: AIResponse,  # pylint: disable=unused-argument
    intent_enum: AnyIntent,  # pylint: disable=unused-argument
    container: ServiceContainer  # pylint: disable=unused-argument
    ) -> None:
    """
    Handles unknown intent - shows help message.
    
    Standardized signature for Dictionary Dispatch Pattern.
    Unused arguments are kept for consistency with other handlers.
    
    Args:
        ctx: Activity context wrapper
        intent: Intent string (unused, kept for signature consistency)
        intent_data: Intent data from AI (unused, kept for signature consistency)
        intent_enum: Intent enum (unused, kept for signature consistency)
        container: Service container (unused, kept for signature consistency)
    """
    language = get_user_language(ctx)
    message = get_translation(TranslationKey.MESSAGE_UNKNOWN_INTENT, language)
    await ctx.send_activity(message)


async def handle_chat_intent(
    ctx: ActivityContextWrapper,
    intent: str,  # pylint: disable=unused-argument
    ai_response: AIResponse,  # pylint: disable=unused-argument
    intent_enum: AnyIntent,  # pylint: disable=unused-argument
    container: ServiceContainer  # pylint: disable=unused-argument
) -> None:
    """
    Handles chat intent - shows bot capabilities.
    
    Standardized signature for Dictionary Dispatch Pattern.
    Can be extended to use AI service for personalized greetings.
    
    Args:
        ctx: Activity context wrapper
        intent: Intent string (unused, kept for signature consistency)
        intent_data: Intent data from AI (unused, kept for signature consistency)
        intent_enum: Intent enum (unused, kept for signature consistency)
        container: Service container (unused now, but available for future AI-powered responses)
    """
    language = get_user_language(ctx)
    
    # Build message with Scheduling capabilities
    message_parts = [get_translation(TranslationKey.MESSAGE_CHAT_GREETING, language)]
    message_parts.append("\n📦 **Scheduling:**")
    message_parts.append("  • Find available time slots")
    message_parts.append("  • Book meetings with Teams links")
    message_parts.append("  • View employee schedules")
    message_parts.append("  • Create workshops and lectures")
    message_parts.append("  • Daily calendar briefing")
    message_parts.append(get_translation(TranslationKey.MESSAGE_CHAT_FOOTER, language))
    
    message = "\n".join(message_parts)
    await ctx.send_activity(message)


async def send_in_development_message(
    ctx: ActivityContextWrapper,
    module_name: str | None = None,
    is_feature: bool = False
) -> None:
    """
    Sends a standardized "in development" message to the user.
    
    Args:
        ctx: Activity context wrapper
        module_name: Optional module name (e.g., "Knowledge Base", "Service Desk")
        is_feature: If True, sends feature-specific message; if False, sends module-specific message
    """
    language = get_user_language(ctx)
    
    if is_feature:
        message = get_translation(TranslationKey.MESSAGE_FEATURE_IN_DEVELOPMENT, language)
    else:
        message = get_translation(
            TranslationKey.MESSAGE_MODULE_IN_DEVELOPMENT,
            language,
            module=module_name or "Unknown"
        )
    
    await ctx.send_activity(message)

