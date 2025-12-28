"""
Router - dispatches messages to appropriate handlers
"""
from typing import Any, Dict
from microsoft.teams.apps import ActivityContext
from enums import BotIntent
from container import ServiceContainer
from handlers.actions import handle_action
from handlers.intents import handle_intent
from handlers.common import handle_unknown_intent, handle_chat_intent


async def route_message(ctx: ActivityContext, container: ServiceContainer) -> None:
    """
    Main router function - determines message type and routes to appropriate handler
    
    Args:
        ctx: Activity context from Teams
        container: Service container with all services
    """
    # Check if this is an action from Adaptive Card (button click)
    if ctx.activity.value and "action" in ctx.activity.value:
        action = ctx.activity.value.get("action", "")
        await handle_action(ctx, action, container)
        return
    
    # This is a text message - detect intent and route
    user_message = ctx.activity.text or ""
    
    if not user_message:
        # Empty message - ignore
        return
    
    # Detect intent using AI
    intent_data = await container.openai_service.detect_intent(user_message)
    intent = intent_data.get("intent", BotIntent.UNKNOWN.value)
    
    # If intent is onboarding, try to parse candidate data first
    if intent == BotIntent.ONBOARDING.value:
        candidate_data = await container.openai_service.parse_candidate_data(user_message)
        
        if candidate_data and "error" not in candidate_data:
            # Found candidate data - add to intent_data and route to onboarding
            intent_data["candidate_data"] = candidate_data
            await handle_intent(ctx, intent, intent_data, container)
            return
    
    # Route to intent handler
    await handle_intent(ctx, intent, intent_data, container)

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                