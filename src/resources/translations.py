"""
Translation resources for bot localization
"""
from typing import Dict
from enums.languages import Language
from enums.bot_module import BotModule
from enums.bot_capability import BotCapability
from enums.bot_intent import BotIntent
from enums.bot_action import BotAction


# Translation dictionaries
TRANSLATIONS: Dict[Language, Dict[str, str]] = {
    Language.ENGLISH: {
        # BotModule names
        "module.people_ops": "People Ops",
        "module.time_off": "Time Off",
        "module.knowledge_base": "Knowledge Base",
        "module.service_desk": "Service Desk",
        
        # BotCapability names
        "capability.create_user": "Create Users",
        "capability.schedule_meeting": "Schedule Meetings",
        "capability.welcome_checklist": "Welcome Checklist",
        "capability.offboarding": "Offboarding",
        "capability.request_vacation": "Request Vacation",
        "capability.approve_vacation": "Approve Vacation",
        "capability.check_vacation_balance": "Check Vacation Balance",
        "capability.answer_question": "Answer Questions from Knowledge Base",
        "capability.request_access": "Request Access",
        "capability.request_equipment": "Request Equipment",
        
        # BotIntent names
        "intent.onboarding": "Create User",
        "intent.schedule_meeting": "Schedule Meeting",
        "intent.welcome_checklist": "Welcome Checklist",
        "intent.offboarding": "Offboarding",
        "intent.request_vacation": "Request Vacation",
        "intent.check_vacation_balance": "Check Vacation Balance",
        "intent.ask_question": "Ask Question",
        "intent.request_access": "Request Access",
        "intent.request_equipment": "Request Equipment",
        "intent.chat": "General Conversation",
        "intent.unknown": "Unknown Intent",
        
        # BotAction names
        "action.create_user": "Create User",
        "action.reject_candidate": "Reject Candidate",
        "action.select_user": "Select User",
        "action.confirm_meeting": "Confirm Meeting",
        "action.regenerate_time": "Regenerate Time",
        "action.complete_checklist_item": "Complete Checklist Item",
        "action.view_checklist_progress": "View Checklist Progress",
        "action.confirm_offboarding": "Confirm Offboarding",
        "action.cancel_offboarding": "Cancel Offboarding",
        "action.approve_vacation": "Approve Vacation",
        "action.reject_vacation": "Reject Vacation",
        "action.approve_access_request": "Approve Access Request",
        "action.reject_access_request": "Reject Access Request",
        "action.approve_equipment_request": "Approve Equipment Request",
        "action.reject_equipment_request": "Reject Equipment Request",
        
        # Messages
        "message.unknown_intent": "🤔 Sorry, I didn't understand your request.\n\nI can help with:\n• Creating accounts for new employees\n• Scheduling meetings\n• Vacation requests (coming soon)\n• Answering questions (coming soon)\n\nPlease rephrase your request or send me a resume to create an account.",
        "message.chat_greeting": "Hello! I'm HR Onboarding Assistant. I can help with:\n",
        "message.chat_footer": "\n\nSend me a resume or candidate data, and I'll help create an account!",
        "message.greeting": "Hello, {name}!",
        "message.user_created": "✅ User **{email}** has been successfully created!",
        "message.meeting_scheduled": "📅 Meeting '{subject}' scheduled for {date} at {time}",
    },
    Language.UKRAINIAN: {
        # BotModule names
        "module.people_ops": "People Ops",
        "module.time_off": "Time Off",
        "module.knowledge_base": "Knowledge Base",
        "module.service_desk": "Service Desk",
        
        # BotCapability names
        "capability.create_user": "Створення користувачів",
        "capability.schedule_meeting": "Призначення зустрічей в календарі",
        "capability.welcome_checklist": "Welcome Checklist",
        "capability.offboarding": "Offboarding (звільнення)",
        "capability.request_vacation": "Запит відпустки",
        "capability.approve_vacation": "Погодження відпустки",
        "capability.check_vacation_balance": "Перевірка балансу відпустки",
        "capability.answer_question": "Відповіді на питання з бази знань",
        "capability.request_access": "Запит доступу",
        "capability.request_equipment": "Запит техніки",
        
        # BotIntent names
        "intent.onboarding": "Створення користувача",
        "intent.schedule_meeting": "Призначення зустрічі",
        "intent.welcome_checklist": "Welcome Checklist",
        "intent.offboarding": "Offboarding (звільнення)",
        "intent.request_vacation": "Запит відпустки",
        "intent.check_vacation_balance": "Перевірка балансу відпустки",
        "intent.ask_question": "Питання з бази знань",
        "intent.request_access": "Запит доступу",
        "intent.request_equipment": "Запит техніки",
        "intent.chat": "Загальна розмова",
        "intent.unknown": "Невідомий намір",
        
        # BotAction names
        "action.create_user": "Створити користувача",
        "action.reject_candidate": "Відхилити кандидата",
        "action.select_user": "Обрати користувача",
        "action.confirm_meeting": "Підтвердити зустріч",
        "action.regenerate_time": "Перегенерувати час",
        "action.complete_checklist_item": "Завершити пункт чеклисту",
        "action.view_checklist_progress": "Переглянути прогрес чеклисту",
        "action.confirm_offboarding": "Підтвердити звільнення",
        "action.cancel_offboarding": "Скасувати звільнення",
        "action.approve_vacation": "Погодити відпустку",
        "action.reject_vacation": "Відхилити відпустку",
        "action.approve_access_request": "Погодити запит доступу",
        "action.reject_access_request": "Відхилити запит доступу",
        "action.approve_equipment_request": "Погодити запит техніки",
        "action.reject_equipment_request": "Відхилити запит техніки",
        
        # Messages
        "message.unknown_intent": "🤔 Вибачте, я не зрозумів ваш запит.\n\nЯ можу допомогти з:\n• Створенням акаунтів для нових співробітників\n• Призначенням зустрічей\n• Запитами відпустки (скоро)\n• Відповідями на питання (скоро)\n\nСпробуйте переформулювати запит або надішліть мені резюме для створення акаунта.",
        "message.chat_greeting": "Привіт! Я HR Onboarding Assistant. Я можу допомогти з:\n",
        "message.chat_footer": "\n\nНадішліть мені резюме або дані про кандидата, і я допоможу створити акаунт!",
        "message.greeting": "Привіт, {name}!",
        "message.user_created": "✅ Користувача **{email}** успішно створено!",
        "message.meeting_scheduled": "📅 Зустріч '{subject}' заплановано на {date} о {time}",
    }
}


def get_translation(key: str, language: Language = Language.ENGLISH, **kwargs) -> str:
    """
    Gets a translation for a given key and language with optional formatting.
    Implements deep fallback: if key is missing in target language, falls back to English.
    
    Args:
        key: Translation key (e.g., "module.people_ops")
        language: Target language
        **kwargs: Variables to format into the translation string (e.g., name="John")
        
    Returns:
        Translated string with formatted variables, or the key itself if translation is not found in any language
        
    Example:
        >>> get_translation("message.greeting", Language.ENGLISH, name="John")
        "Hello, John!"
    """
    if not key:
        return key
    
    # Try to get translation from target language
    translations = TRANSLATIONS.get(language)
    text = None
    
    if translations:
        text = translations.get(key)
    
    # Deep fallback: if not found in target language, try English
    if text is None and language != Language.ENGLISH:
        english_translations = TRANSLATIONS.get(Language.ENGLISH)
        if english_translations:
            text = english_translations.get(key)
            if text:
                print(f"⚠️ Translation key '{key}' not found in {language.value}, using English fallback")
    
    # If still not found, return the key itself
    if text is None:
        print(f"⚠️ Translation key '{key}' not found in any language, returning key")
        text = key
    
    # Format the string if kwargs are provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError as e:
            # If a format key is missing, log and return unformatted text
            print(f"⚠️ Missing format key {e} in translation '{key}'")
        except Exception as e:
            # If formatting fails for any reason, return unformatted text
            print(f"⚠️ Formatting error for translation '{key}': {e}")
    
    return text


def get_module_name(module: BotModule, language: Language = Language.ENGLISH, **kwargs) -> str:
    """
    Gets the translated name for a BotModule
    
    Args:
        module: BotModule enum value (can be None)
        language: Target language
        **kwargs: Optional variables to format into the translation string
        
    Returns:
        Translated module name, or empty string if module is None
    """
    if module is None:
        return ""
    key = f"module.{module.value}"
    return get_translation(key, language, **kwargs)


def get_capability_name(capability: BotCapability, language: Language = Language.ENGLISH, **kwargs) -> str:
    """
    Gets the translated name for a BotCapability
    
    Args:
        capability: BotCapability enum value (can be None)
        language: Target language
        **kwargs: Optional variables to format into the translation string
        
    Returns:
        Translated capability name, or empty string if capability is None
    """
    if capability is None:
        return ""
    key = f"capability.{capability.value}"
    return get_translation(key, language, **kwargs)


def get_intent_name(intent: BotIntent, language: Language = Language.ENGLISH, **kwargs) -> str:
    """
    Gets the translated name for a BotIntent
    
    Args:
        intent: BotIntent enum value (can be None)
        language: Target language
        **kwargs: Optional variables to format into the translation string
        
    Returns:
        Translated intent name, or "Unknown" if intent is None
    """
    if intent is None:
        return get_translation("intent.unknown", language, **kwargs)
    key = f"intent.{intent.value}"
    return get_translation(key, language, **kwargs)


def get_action_name(action: BotAction, language: Language = Language.ENGLISH, **kwargs) -> str:
    """
    Gets the translated name for a BotAction
    
    Args:
        action: BotAction enum value (can be None)
        language: Target language
        **kwargs: Optional variables to format into the translation string
        
    Returns:
        Translated action name, or empty string if action is None
    """
    if action is None:
        return ""
    key = f"action.{action.value}"
    return get_translation(key, language, **kwargs)

