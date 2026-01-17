"""
Translation resources for bot localization
"""
from typing import Dict, Union
from core.enums.languages import Language
from core.enums.bot import BotModule, BotIntent
from core.enums.bot import BotAction
from core.enums.translation_key import TranslationKey


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
        "message.unknown_intent": "🤔 Sorry, I didn't understand your request.\n\nI can help with:\n\n📦 **Scheduling:**\n• Find available time slots\n• Book meetings with Teams links\n• View employee schedules\n• Create workshops and lectures\n• Daily calendar briefing\n\n📋 **People Ops:**\n• Creating accounts for new employees (coming soon)\n• Welcome checklists (coming soon)\n• Offboarding (coming soon)\n\n⏰ **Time Off:**\n• Vacation requests (coming soon)\n• Check vacation balance (coming soon)\n\n💬 **Knowledge Base:**\n• Answering questions (coming soon)\n\nPlease rephrase your request or try one of the options above.",
        "message.chat_greeting": "Hello! I'm HR Onboarding Assistant. I can help with:\n",
        "message.chat_scheduling_capabilities": "\n📦 **Scheduling:**\n  • Find available time slots\n  • Book meetings with Teams links\n  • View employee schedules\n  • Create workshops and lectures\n  • Daily calendar briefing",
        "message.chat_footer": "\n\nSend me a resume or candidate data, and I'll help create an account!",
        "message.greeting": "Hello, {name}!",
        "message.user_created": "✅ User **{email}** has been successfully created!",
        "message.meeting_scheduled": "📅 Meeting '{subject}' scheduled for {date} at {time}",
        "message.module_in_development": "⚠️ {module} module is under development",
        "message.feature_in_development": "⚠️ This feature is under development",
        "message.processing_error": "Sorry, an error occurred while processing your message. Please try again.",
        "message.user_identification_error": "❌ Error: Unable to identify user. Please contact support.",
        
        # Time Off
        "time_off.balance_title": "Leave Balance - {name}",
        "time_off.vacation_balance": "Vacation Days:",
        "time_off.sick_balance": "Sick Leave Days:",
        "time_off.vacation": "Vacation",
        "time_off.sick_leave": "Sick Leave",
        "time_off.employee_not_found": "❌ Employee not found. Please contact HR.",
        "time_off.invalid_start_date": "❌ Invalid start date. Please use format: YYYY-MM-DD, 'tomorrow', or 'next Monday'.",
        "time_off.invalid_end_date": "❌ Invalid end date. Please use format: YYYY-MM-DD or specify duration.",
        "time_off.past_date_error": "❌ Start date cannot be in the past for vacation requests.",
        "time_off.insufficient_balance": "❌ Insufficient balance. You requested {requested} days of {type}, but only {available} days are available.",
        "time_off.date_overlap_error": "❌ These dates overlap with an existing approved leave request.",
        "time_off.request_created": "✅ Leave request created: {days} days from {start_date} to {end_date}. Waiting for manager approval.",
        "time_off.request_not_found": "❌ Leave request not found.",
        "time_off.request_already_processed": "⚠️ This request has already been processed.",
        "time_off.request_approved": "✅ Leave request approved! Calendar event created.",
        "time_off.request_rejected": "❌ Leave request rejected. {reason}",
        "time_off.parse_error": "❌ Could not parse leave request: {error}",
        "time_off.unknown_intent": "❌ Unknown time off request. Please specify: vacation, sick leave, or check balance.",
        "time_off.no_pending_requests": "✅ No pending leave requests to approve.",
        "time_off.pending_requests_title": "Pending Leave Requests",
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
        "message.unknown_intent": "🤔 Вибачте, я не зрозумів ваш запит.\n\nЯ можу допомогти з:\n\n📦 **Scheduling:**\n• Знайти доступні часові слоти\n• Забронювати зустрічі з посиланнями Teams\n• Переглянути розклади співробітників\n• Створити воркшопи та лекції\n• Щоденний брифінг календаря\n\n📋 **People Ops:**\n• Створення акаунтів для нових співробітників (скоро)\n• Welcome checklists (скоро)\n• Offboarding (скоро)\n\n⏰ **Time Off:**\n• Запити відпустки (скоро)\n• Перевірка балансу відпустки (скоро)\n\n💬 **Knowledge Base:**\n• Відповіді на питання (скоро)\n\nСпробуйте переформулювати запит або оберіть один з варіантів вище.",
        "message.chat_greeting": "Привіт! Я HR Onboarding Assistant. Я можу допомогти з:\n",
        "message.chat_scheduling_capabilities": "\n📦 **Scheduling:**\n  • Знайти доступні часові слоти\n  • Забронювати зустрічі з посиланнями Teams\n  • Переглянути розклади співробітників\n  • Створити воркшопи та лекції\n  • Щоденний брифінг календаря",
        "message.chat_footer": "\n\nНадішліть мені резюме або дані про кандидата, і я допоможу створити акаунт!",
        "message.greeting": "Привіт, {name}!",
        "message.user_created": "✅ Користувача **{email}** успішно створено!",
        "message.meeting_scheduled": "📅 Зустріч '{subject}' заплановано на {date} о {time}",
        "message.module_in_development": "⚠️ Модуль {module} в розробці",
        "message.feature_in_development": "⚠️ Ця функція в розробці",
        "message.processing_error": "Вибачте, сталася помилка при обробці вашого повідомлення. Будь ласка, спробуйте ще раз.",
        "message.user_identification_error": "❌ Помилка: не вдалося ідентифікувати користувача. Зверніться до підтримки.",
        
        # Time Off
        "time_off.balance_title": "Баланс відпусток - {name}",
        "time_off.vacation_balance": "Днів відпустки:",
        "time_off.sick_balance": "Днів лікарняних:",
        "time_off.vacation": "Відпустка",
        "time_off.sick_leave": "Лікарняний",
        "time_off.employee_not_found": "❌ Співробітника не знайдено. Зверніться до HR.",
        "time_off.invalid_start_date": "❌ Невірна дата початку. Використовуйте формат: YYYY-MM-DD, 'завтра' або 'наступний понеділок'.",
        "time_off.invalid_end_date": "❌ Невірна дата завершення. Використовуйте формат: YYYY-MM-DD або вкажіть тривалість.",
        "time_off.past_date_error": "❌ Дата початку не може бути в минулому для заявок на відпустку.",
        "time_off.insufficient_balance": "❌ Недостатньо днів. Ви запитуєте {requested} днів {type}, але доступно лише {available}.",
        "time_off.date_overlap_error": "❌ Ці дати перетинаються з існуючою затвердженою заявкою.",
        "time_off.request_created": "✅ Заявку створено: {days} днів з {start_date} по {end_date}. Очікується підтвердження керівника.",
        "time_off.request_not_found": "❌ Заявку не знайдено.",
        "time_off.request_already_processed": "⚠️ Ця заявка вже оброблена.",
        "time_off.request_approved": "✅ Заявку підтверджено! Подію в календарі створено.",
        "time_off.request_rejected": "❌ Заявку відхилено. {reason}",
        "time_off.parse_error": "❌ Не вдалося розпізнати заявку: {error}",
        "time_off.unknown_intent": "❌ Невідомий запит. Вкажіть: відпустка, лікарняний або перевірка балансу.",
        "time_off.no_pending_requests": "✅ Немає заявок на відпустку, що очікують на погодження.",
        "time_off.pending_requests_title": "Заявки на погодження",
    }
}


def get_translation(
    key: Union[str, TranslationKey], 
    language: Language = Language.ENGLISH, 
    **kwargs
) -> str:
    """
    Gets a translation for a given key and language with optional formatting.
    Implements deep fallback: if key is missing in target language, falls back to English.
    
    Args:
        key: Translation key (string or TranslationKey enum)
            Examples: "message.greeting" or TranslationKey.MESSAGE_GREETING
        language: Target language
        **kwargs: Variables to format into the translation string (e.g., name="John")
        
    Returns:
        Translated string with formatted variables, or the key itself if translation is not found in any language
        
    Example:
        >>> get_translation("message.greeting", Language.ENGLISH, name="John")
        "Hello, John!"
        >>> get_translation(TranslationKey.MESSAGE_GREETING, Language.ENGLISH, name="John")
        "Hello, John!"
    """
    # Convert TranslationKey enum to string if needed
    key_str = key.value if isinstance(key, TranslationKey) else str(key)
    
    if not key_str:
        return key_str
    
    # Try to get translation from target language
    translations = TRANSLATIONS.get(language)
    text = None
    
    # Use key_str instead of key from now on
    key = key_str
    
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


def get_intent_name(intent: BotIntent, language: Language = Language.ENGLISH, **kwargs) -> str:
    """
    Gets the translated name for an intent
    
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

