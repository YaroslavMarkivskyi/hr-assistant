import logging
from typing import Any

from botbuilder.core import TurnContext
from botbuilder.schema import ActivityTypes

from core.enums.bot import (
    BotRequestType, 
    BotAction, 
    BotIntent, 
    get_action_enum_instance,
    get_intent_enum_instance
)
from core.extraction_registry import EXTRACTOR_REGISTRY

from schemas.bot import ClassifiedRequest, ActionPayload, IntentPayload

from services.ai import AIService


logger = logging.getLogger(__name__)


class RequestClassifier:
    def __init__(self, ai_service: AIService) -> None:
        self._ai_service = ai_service
        
    async def classify(self, turn_context: TurnContext) -> ClassifiedRequest:
        activity = turn_context.activity
        
        if activity.value and (activity.type == ActivityTypes.message or activity.type == ActivityTypes.invoke):
            return await self._classify_action(activity.value)
        
        if activity.type == ActivityTypes.message and activity.text:
            return await self._classify_intent(activity.text)
        
        return ClassifiedRequest(
            request_type=BotRequestType.INTENT,
            payload=IntentPayload(
                intent=BotIntent.UNKNOWN,
                confidence=0.0,
                original_text=""
            )
        )
    
    async def _classify_action(self, value: Any) -> ClassifiedRequest:
        action_name = value.get("action")
        data = value.get("data", {})
        
        action_enum = get_action_enum_instance(str(action_name)) or BotAction.UNKNOWN
        
        if action_enum == BotAction.UNKNOWN:
            logger.warning(f"Received unknown action: {action_name}")
        
        payload = ActionPayload(
            action=action_enum,
            data=data
        )
        return ClassifiedRequest(
            request_type=BotRequestType.ACTION,
            payload=payload
        )
        
            
    async def _classify_intent(self, text: str) -> ClassifiedRequest:
        # TODO: In future, we can give context such as user profile, conversation history, previous interactions, etc.
        user_intent = await self._ai_service.detect_intent(
            user_text=text,
            context=None,
        )
        
        bot_intent = get_intent_enum_instance(user_intent.intent) or BotIntent.UNKNOWN
        
        if bot_intent == BotIntent.UNKNOWN:
            logger.warning(f"Received unknown intent: {user_intent.intent}")
        
        entities_data = {}
        
        config = EXTRACTOR_REGISTRY.get(bot_intent)
        
        if config:
            logger.info(f"Extracting data for intent {bot_intent} using schema {config.schema.__name__}")
            extracted_data = await self._ai_service.extract_data(
                user_text=text,
                result_type=config.schema,
                prompt_key=config.prompt_key,
                context=None
            )

            entities_data = extracted_data.model_dump(exclude_unset=True)
            
        payload = IntentPayload(
            intent=bot_intent,
            confidence=user_intent.confidence,
            language=user_intent.language,
            original_text=text,
            entities=entities_data
        )
        return ClassifiedRequest(
            request_type=BotRequestType.INTENT,
            payload=payload
        )
        
__all__ = ("RequestClassifier",)

