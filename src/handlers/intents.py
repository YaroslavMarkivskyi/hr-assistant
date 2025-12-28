"""
Handler for user intents (AI-detected intents)
"""
from typing import Dict, Any
from microsoft.teams.apps import ActivityContext
from enums import BotIntent, BotModule
from container import ServiceContainer
import features.onboarding as onboarding_feature
import features.calendar as calendar_feature
from utils.helpers import get_user_language


async def handle_intent(
    ctx: ActivityContext, 
    intent: str, 
    intent_data: Dict[str, Any],
    container: ServiceContainer
) -> None:
    """
    Handles user intents detected by AI
    
    Args:
        ctx: Activity context from Teams
        intent: Intent string (e.g., "onboarding", "schedule_meeting")
        intent_data: Full intent data from AI (may include entities, candidate_data, etc.)
        container: Service container with all services
    """
    # Find the intent enum
    intent_enum = None
    for intent_item in BotIntent:
        if intent_item.value == intent:
            intent_enum = intent_item
            break
    
    if not intent_enum:
        await handle_unknown_intent(ctx)
        return
    
    module = intent_enum.get_module()
    
    # Route by module
    if module == BotModule.PEOPLE_OPS:
        await _handle_people_ops_intent(ctx, intent, intent_data, intent_enum, container)
    elif module == BotModule.TIME_OFF:
        await _handle_time_off_intent(ctx, intent, container)
    elif module == BotModule.KNOWLEDGE_BASE:
        await _handle_knowledge_base_intent(ctx, intent, container)
    elif module == BotModule.SERVICE_DESK:
        await _handle_service_desk_intent(ctx, intent, container)
    else:
        # Intent doesn't belong to any module (e.g., CHAT, UNKNOWN)
        if intent == BotIntent.UNKNOWN.value:
            await handle_unknown_intent(ctx)
        elif intent == BotIntent.CHAT.value:
            await handle_chat_intent(ctx)


async def _handle_people_ops_intent(
    ctx: ActivityContext,
    intent: str,
    intent_data: Dict[str, Any],
    intent_enum: BotIntent,
    container: ServiceContainer
) -> None:
    """Handles People Ops module intents"""
    if intent == BotIntent.ONBOARDING.value:
        await onboarding_feature.run_flow(
            ctx,
            intent_data,
            container.openai_service,
            container.graph_service,
            container.email_service
        )
    elif intent == BotIntent.SCHEDULE_MEETING.value:
        requester_id = _get_requester_id(ctx, container.config)
        await calendar_feature.run_flow(
            ctx,
            intent_data,
            container.openai_service,
            container.graph_service,
            requester_id
        )
    # TODO: Add welcome_checklist and offboarding intents
    elif intent in [BotIntent.WELCOME_CHECKLIST.value, BotIntent.OFFBOARDING.value]:
        from resources import get_translation
        language = get_user_language(ctx)
        await ctx.send(get_translation("message.feature_in_development", language))


async def _handle_time_off_intent(ctx: ActivityContext, intent: str, container: ServiceContainer) -> None:
    """Handles Time Off module intents"""
    # TODO: Implement Time Off intent handling
    from resources import get_translation
    language = get_user_language(ctx)
    await ctx.send(get_translation("message.module_in_development", language, module="Time Off"))


async def _handle_knowledge_base_intent(ctx: ActivityContext, intent: str, container: ServiceContainer) -> None:
    """Handles Knowledge Base module intents"""
    # TODO: Implement Knowledge Base intent handling
    from resources import get_translation
    language = get_user_language(ctx)
    await ctx.send(get_translation("message.module_in_development", language, module="Knowledge Base"))


async def _handle_service_desk_intent(ctx: ActivityContext, intent: str, container: ServiceContainer) -> None:
    """Handles Service Desk module intents"""
    # TODO: Implement Service Desk intent handling
    from resources import get_translation
    language = get_user_language(ctx)
    await ctx.send(get_translation("message.module_in_development", language, module="Service Desk"))


def _get_requester_id(ctx: ActivityContext, config) -> str | None:
    """Extracts requester ID from activity context"""
    requester_id = None
    if hasattr(ctx.activity, 'from_property') and ctx.activity.from_property:
        requester_id = getattr(ctx.activity.from_property, 'aad_object_id', None) or getattr(ctx.activity.from_property, 'id', None)
    
    # For local testing: use test ID if requester_id not found
    if not requester_id and config.TEST_USER_ID:
        requester_id = config.TEST_USER_ID
        print(f"🧪 Using test requester_id: {requester_id}")
    elif not requester_id:
        print("⚠️ Requester ID not found. User will not be added as participant automatically.")
    
    return requester_id

