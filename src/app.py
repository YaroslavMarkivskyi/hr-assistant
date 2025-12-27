import asyncio
from typing import Any

from azure.identity import ManagedIdentityCredential
from botbuilder.core import MemoryStorage
from microsoft.teams.apps import App, ActivityContext

# --- ІМПОРТИ ---
from config import Config
from enums import BotIntent, BotAction, BotCapability, BotModule, Language
from resources import get_module_name, get_capability_name, get_intent_name, get_action_name, get_translation
from services.graph_service import GraphService
from services.email_service import EmailService
from services.openai_service import OpenAIService

# Імпортуємо модулі
# People Ops (існуючі фічі)
import features.onboarding as onboarding_feature
import features.calendar as calendar_feature

# Інші модулі (будуть реалізовані)
# from modules.time_off import request_vacation, approve_reject, balance
# from modules.knowledge_base import qa
# from modules.service_desk import request_access, request_equipment
# from modules.people_ops import welcome_checklist, offboarding

config = Config()

# --- ІНІЦІАЛІЗАЦІЯ ---
def create_token_factory():
    def get_token(scopes, tenant_id=None):
        credential = ManagedIdentityCredential(client_id=config.APP_ID)
        token = credential.get_token(*(scopes if not isinstance(scopes, str) else [scopes]))
        return token.token
    return get_token

storage = MemoryStorage()

app = App(
    token=create_token_factory() if config.APP_TYPE == "UserAssignedMsi" else None,
    storage=storage
)

# Ініціалізуємо сервіси
graph_service = GraphService(config)
email_service = EmailService(config)
openai_service = OpenAIService(config)

# --- РОУТЕР ---
def get_user_language(ctx: ActivityContext) -> Language:
    """
    Gets user language from Teams context
    
    Args:
        ctx: Activity context from Teams
        
    Returns:
        Language enum based on user's Teams locale
    """
    locale = None
    if hasattr(ctx.activity, 'locale') and ctx.activity.locale:
        locale = ctx.activity.locale
    elif hasattr(ctx.activity, 'from_property') and ctx.activity.from_property:
        # Try to get locale from user properties if available
        locale = getattr(ctx.activity.from_property, 'locale', None)
    
    return Language.from_locale(locale or "")

@app.on_message
async def handle_message(ctx: ActivityContext, state: Any = None):
    """Main router: determines intent and routes to appropriate feature"""
    
    # 0. Перевіряємо, чи це дія з картки (натискання кнопки)
    if ctx.activity.value and "action" in ctx.activity.value:
        action = ctx.activity.value.get("action", "")
        
        # Визначаємо модуль дії та маршрутизуємо
        action_enum = None
        for act in BotAction:
            if act.value == action:
                action_enum = act
                break
        
        if action_enum:
            module = action_enum.get_module()
            
            # Маршрутизація по модулях
            if module == BotModule.PEOPLE_OPS:
                # People Ops модуль
                onboarding_actions = [a.value for a in BotAction.get_onboarding_actions()]
                calendar_actions = [a.value for a in BotAction.get_calendar_actions()]
                
                if action in onboarding_actions:
                    # Дія з картки онбордингу
                    intent_data = {"intent": BotIntent.ONBOARDING.value, "entities": {}}
                    await onboarding_feature.run_flow(
                        ctx, 
                        intent_data, 
                        openai_service, 
                        graph_service, 
                        email_service
                    )
                elif action in calendar_actions:
                    # Дія з картки календаря
                    intent_data = {"intent": BotIntent.SCHEDULE_MEETING.value, "entities": {}}
                    # Отримуємо ID користувача з activity
                    requester_id = None
                    if hasattr(ctx.activity, 'from_property') and ctx.activity.from_property:
                        requester_id = getattr(ctx.activity.from_property, 'aad_object_id', None) or getattr(ctx.activity.from_property, 'id', None)
                    await calendar_feature.run_flow(
                        ctx, 
                        intent_data,
                        openai_service,
                        graph_service,
                        requester_id
                    )
                # TODO: Додати обробку welcome_checklist та offboarding дій
                
            elif module == BotModule.TIME_OFF:
                # TODO: Реалізувати обробку Time Off дій
                await ctx.send("⚠️ Модуль Time Off в розробці")
                
            elif module == BotModule.SERVICE_DESK:
                # TODO: Реалізувати обробку Service Desk дій
                await ctx.send("⚠️ Модуль Service Desk в розробці")
                
            else:
                await ctx.send(f"⚠️ Невідомий модуль для дії: {action}")
        return
    
    user_message = ctx.activity.text or ""
    
    # 1. Спочатку визначаємо намір через LLM (щоб розрізнити новий запит від продовження)
    if not user_message:
        # Порожнє повідомлення - не обробляємо
        return
    
    # Визначаємо намір перед парсингом кандидата
    intent_data = await openai_service.detect_intent(user_message)
    intent = intent_data.get("intent", BotIntent.UNKNOWN.value)
    
    # Якщо намір явно не onboarding - не парсимо як кандидата
    # Це дозволяє обробляти нові запити після завершення флоу
    if intent == BotIntent.ONBOARDING.value:
        # Тільки якщо намір onboarding - парсимо дані кандидата
        candidate_data = await openai_service.parse_candidate_data(user_message)
        
        if candidate_data and "error" not in candidate_data:
            # Знайшли дані кандидата - одразу onboarding
            intent_data["candidate_data"] = candidate_data
            await onboarding_feature.run_flow(
                ctx, 
                intent_data, 
                openai_service, 
                graph_service, 
                email_service
            )
            return
    
    # 2. Маршрутизація (Router) - intent вже визначено вище
    # Визначаємо модуль для intent
    intent_enum = None
    for intent_item in BotIntent:
        if intent_item.value == intent:
            intent_enum = intent_item
            break
    
    if intent_enum and intent_enum.get_module():
        module = intent_enum.get_module()
        
        # Маршрутизація по модулях
        if module == BotModule.PEOPLE_OPS:
            # People Ops модуль
            if intent == BotIntent.ONBOARDING.value:
                await onboarding_feature.run_flow(
                    ctx, 
                    intent_data, 
                    openai_service, 
                    graph_service, 
                    email_service
                )
            elif intent == BotIntent.SCHEDULE_MEETING.value:
                # Отримуємо ID користувача з activity
                requester_id = None
                if hasattr(ctx.activity, 'from_property') and ctx.activity.from_property:
                    requester_id = getattr(ctx.activity.from_property, 'aad_object_id', None) or getattr(ctx.activity.from_property, 'id', None)
                
                # Для локального тестування: якщо requester_id не знайдено, використовуємо тестовий ID
                if not requester_id and config.TEST_USER_ID:
                    requester_id = config.TEST_USER_ID
                    print(f"🧪 Використовую тестовий requester_id: {requester_id}")
                elif not requester_id:
                    print("⚠️ Requester ID не знайдено. Користувач не буде додано як учасник автоматично.")
                
                await calendar_feature.run_flow(
                    ctx, 
                    intent_data,
                    openai_service,
                    graph_service,
                    requester_id
                )
            # TODO: Додати обробку welcome_checklist та offboarding intent
            elif intent in [BotIntent.WELCOME_CHECKLIST.value, BotIntent.OFFBOARDING.value]:
                await ctx.send("⚠️ Ця функція в розробці")
                
        elif module == BotModule.TIME_OFF:
            # TODO: Реалізувати обробку Time Off intent
            await ctx.send("⚠️ Модуль Time Off в розробці")
            
        elif module == BotModule.KNOWLEDGE_BASE:
            # TODO: Реалізувати обробку Knowledge Base intent
            await ctx.send("⚠️ Модуль Knowledge Base в розробці")
            
        elif module == BotModule.SERVICE_DESK:
            # TODO: Реалізувати обробку Service Desk intent
            await ctx.send("⚠️ Модуль Service Desk в розробці")
            
    elif intent == BotIntent.UNKNOWN.value:
        # Unknown intent - show help
        language = get_user_language(ctx)
        message = get_translation("message.unknown_intent", language)
        await ctx.send(message)
    elif intent == BotIntent.CHAT.value:
        # Standard chat response
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
    else:
        # Fallback для будь-яких інших випадків
        await ctx.send("Вибачте, я не зрозумів ваш запит. Спробуйте ще раз.")

if __name__ == "__main__":
    asyncio.run(app.start())
