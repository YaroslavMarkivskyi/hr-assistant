"""
Handler for Adaptive Card actions (button clicks)
"""
from typing import Dict, Any
from microsoft.teams.apps import ActivityContext
from enums import BotAction, BotModule, BotIntent
from container import ServiceContainer
import features.onboarding as onboarding_feature
import features.calendar as calendar_feature


async def handle_action(ctx: ActivityContext, action: str, container: ServiceContainer) -> None:
    """
    Handles actions from Adaptive Cards (button clicks)
    
    Args:
        ctx: Activity context from Teams
        action: Action string from the card
        container: Service container with all services
    """
    # Find the action enum
    action_enum = None
    for act in BotAction:
        if act.value == action:
            action_enum = act
            break
    
    if not action_enum:
        from utils.helpers import get_user_language
        from resources import get_translation
        language = get_user_language(ctx)
        await ctx.send(get_translation("message.unhandled_request", language))
        return
    
    module = action_enum.get_module()
    
    # Route by module
    if module == BotModule.PEOPLE_OPS:
        await _handle_people_ops_action(ctx, action, action_enum, container)
    elif module == BotModule.TIME_OFF:
        await _handle_time_off_action(ctx, action, container)
    elif module == BotModule.SERVICE_DESK:
        await _handle_service_desk_action(ctx, action, container)
    else:
        from utils.helpers import get_user_language
        from resources import get_translation
        language = get_user_language(ctx)
        await ctx.send(get_translation("message.unhandled_request", language))


async def _handle_people_ops_action(
    ctx: ActivityContext, 
    action: str, 
    action_enum: BotAction,
    container: ServiceContainer
) -> None:
    """Handles People Ops module actions"""
    onboarding_actions = [a.value for a in BotAction.get_onboarding_actions()]
    calendar_actions = [a.value for a in BotAction.get_calendar_actions()]
    
    if action in onboarding_actions:
        # Onboarding action
        intent_data = {"intent": BotIntent.ONBOARDING.value, "entities": {}}
        await onboarding_feature.run_flow(
            ctx,
            intent_data,
            container.openai_service,
            container.graph_service,
            container.email_service
        )
    elif action in calendar_actions:
        # Calendar action
        intent_data = {"intent": BotIntent.SCHEDULE_MEETING.value, "entities": {}}
        requester_id = _get_requester_id(ctx, container.config)
        await calendar_feature.run_flow(
            ctx,
            intent_data,
            container.openai_service,
            container.graph_service,
            requester_id
        )
    # TODO: Add welcome_checklist and offboarding actions


async def _handle_time_off_action(ctx: ActivityContext, action: str, container: ServiceContainer) -> None:
    """Handles Time Off module actions"""
    # TODO: Implement Time Off action handling
    from resources import get_translation
    from utils.helpers import get_user_language
    language = get_user_language(ctx)
    await ctx.send(get_translation("message.module_in_development", language, module="Time Off"))


async def _handle_service_desk_action(ctx: ActivityContext, action: str, container: ServiceContainer) -> None:
    """Handles Service Desk module actions"""
    # TODO: Implement Service Desk action handling
    from resources import get_translation
    from utils.helpers import get_user_language
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

