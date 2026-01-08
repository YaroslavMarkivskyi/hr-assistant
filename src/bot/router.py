"""
Router - dispatches messages to appropriate handlers

This module is part of the bot's message processing logic.
It determines message type (ACTION vs TEXT) and routes to appropriate handlers.

The router's responsibility is ONLY routing - it should not contain business logic.
All intent-specific processing (like parsing candidate data) should be in handlers.
"""
import logging

from bot.activity_context_wrapper import ActivityContextWrapper
from enums.bot import GeneralIntent
from enums.translation_key import TranslationKey
from container import ServiceContainer
from models.action import ActionPayload
from models.ai import AIResponse
from utils.helpers import get_user_language
from resources import get_translation

from schemas.ai import UserIntent

logger = logging.getLogger("HRBot")


class MessageRouter:
    """
    Orchestrates routing of incoming messages.

    Uses explicit type checking to determine handling strategy.
    """

    def __init__(self, ctx: ActivityContextWrapper, container: ServiceContainer) -> None:
        self.ctx = ctx
        self.container = container

    async def route(self) -> None:
        """
        Entry point: Explicitly determines message type and routes accordingly.
        """
        # 1. PURE LOGIC: Determine the type of the message
        is_action = self._is_card_action()
        is_text = self._has_text_content()

        # 2. ROUTING: Dispatch based on type
        if is_action:
            logger.info("⚡ Detected ACTION payload. Routing to Action Handler.")
            await self._process_card_action()

        elif is_text:
            logger.info("📝 Detected TEXT message. Routing to AI Handler.")
            await self._process_text_message()

        else:
            # 3. IGNORE: Neither text nor action (e.g. strict system events or empty inputs)
            logger.debug(
                f"⚠️ Undetermined message type. "
                f"Value: {type(self.ctx.activity.value)}, "
                f"Text present: {bool(self.ctx.activity.text)}"
            )

    # =========================================================================
    # TYPE CHECKERS (Identification)
    # =========================================================================

    def _is_card_action(self) -> bool:
        """Checks if the activity contains a dictionary payload (Adaptive Card Action)."""
        value = self.ctx.activity.value
        return value is not None and isinstance(value, dict)

    def _has_text_content(self) -> bool:
        """Checks if the activity contains valid user text."""
        text = self.ctx.activity.text
        return text is not None and len(text.strip()) > 0

    # =========================================================================
    # PROCESSORS (Execution)
    # =========================================================================

    async def _process_card_action(self) -> None:
        """
        Handles the execution of a card action.

        Stops here even if validation fails (does NOT fall back to text).
        """
        # 1. VALIDATION: Parse and validate payload structure
        raw_value = self.ctx.activity.value
        try:
            payload = ActionPayload.model_validate(raw_value)
        except Exception as validation_error:
            # Якщо це виглядало як Action, але мало криві дані - це помилка розробника або UI.
            # Ми НЕ відправляємо це в AI як текст. Ми просто логуємо помилку.
            logger.error(
                f"❌ Invalid action payload structure: {validation_error}",
                exc_info=True
            )
            return

        # 2. EXECUTION: Route to action handler via dispatcher
        logger.info(f"🔄 Routing ACTION: {payload.action}")
        try:
            await self.container.dispatcher.dispatch_action(
                self.ctx, payload, self.container
            )
        except Exception as execution_error:
            # Помилка під час виконання (БД, мережа, тощо) - не валідація!
            logger.error(
                f"❌ Action execution failed for '{payload.action}': {execution_error}",
                exc_info=True
            )

    async def _process_text_message(self) -> None:
        """
        Handles the AI flow for text messages.
        """
        user_message = self.ctx.activity.text.strip()  # type: ignore (checked in _has_text_content)

        await self._send_typing_indicator()

        user_intent = await self._detect_intent(user_message)

        if not user_intent:
            return

        await self.container.dispatcher.dispatch_intent(
            self.ctx,  
            user_intent, 
            self.container
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    async def _send_typing_indicator(self) -> None:
        """Sends typing indicator before potentially long-running AI calls."""
        try:
            await self.ctx.send_typing_activity()
        except Exception as e:
            logger.debug(f"⚠️ Silent typing indicator fail: {e}")

    async def _detect_intent(self, user_message: str) -> UserIntent | None:
        """Detects and validates intent via AI."""
        logger.info(f"🤖 Detecting intent for: {user_message[:50]}...")

        try:
            intent_data = await self.container.ai_service.detect_intent(user_message)
       
            if hasattr(self.ctx.activity, 'locale'):
                locale_map = {
                    "en": "en-US",
                    "uk": "uk-UA"
                }
                self.ctx.activity.locale = locale_map.get(intent_data.language, "en-US")
                logger.info(f"🌐 Language detected: {intent_data.language} -> locale: {self.ctx.activity.locale}")

            logger.info(f"✅ Intent detected: {intent_data.intent} (module={intent_data.module}, language={intent_data.language})")
            return intent_data

        except Exception as e:
            logger.error(f"❌ AI/Validation failed: {e}", exc_info=True)
            await self._send_processing_error_message()
            return None

    async def _send_processing_error_message(self) -> None:
        """Sends a localized, user-friendly error message when intent detection fails."""
        try:
            language = get_user_language(self.ctx)
            msg = get_translation(TranslationKey.MESSAGE_PROCESSING_ERROR, language)
            await self.ctx.send_activity(msg)
        except Exception as e:
            logger.error(f"❌ Failed to send error message: {e}")
