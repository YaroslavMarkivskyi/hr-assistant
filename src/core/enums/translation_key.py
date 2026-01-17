"""
Translation keys for localization

StrEnum for type-safe translation keys.
Prevents typos and provides IDE autocomplete.
"""
from enum import StrEnum


class TranslationKey(StrEnum):
    """
    Translation keys for bot messages.
    
    Usage:
        from enums.translation_key import TranslationKey
        from resources import get_translation
        
        message = get_translation(TranslationKey.MESSAGE_PROCESSING_ERROR, language)
    """
    
    # Message keys
    MESSAGE_UNKNOWN_INTENT = "message.unknown_intent"
    MESSAGE_CHAT_GREETING = "message.chat_greeting"
    MESSAGE_CHAT_FOOTER = "message.chat_footer"
    MESSAGE_CHAT_SCHEDULING_CAPABILITIES = "message.chat_scheduling_capabilities"
    MESSAGE_GREETING = "message.greeting"
    MESSAGE_USER_CREATED = "message.user_created"
    MESSAGE_MEETING_SCHEDULED = "message.meeting_scheduled"
    MESSAGE_MODULE_IN_DEVELOPMENT = "message.module_in_development"
    MESSAGE_FEATURE_IN_DEVELOPMENT = "message.feature_in_development"
    MESSAGE_PROCESSING_ERROR = "message.processing_error"
    MESSAGE_UNHANDLED_REQUEST = "message.unhandled_request"
    MESSAGE_USER_IDENTIFICATION_ERROR = "message.user_identification_error"
    
    # Time Off keys
    TIME_OFF_BALANCE_TITLE = "time_off.balance_title"
    TIME_OFF_VACATION_BALANCE = "time_off.vacation_balance"
    TIME_OFF_SICK_BALANCE = "time_off.sick_balance"
    TIME_OFF_VACATION = "time_off.vacation"
    TIME_OFF_SICK_LEAVE = "time_off.sick_leave"
    TIME_OFF_EMPLOYEE_NOT_FOUND = "time_off.employee_not_found"
    TIME_OFF_INVALID_START_DATE = "time_off.invalid_start_date"
    TIME_OFF_INVALID_END_DATE = "time_off.invalid_end_date"
    TIME_OFF_PAST_DATE_ERROR = "time_off.past_date_error"
    TIME_OFF_INSUFFICIENT_BALANCE = "time_off.insufficient_balance"
    TIME_OFF_DATE_OVERLAP_ERROR = "time_off.date_overlap_error"
    TIME_OFF_REQUEST_CREATED = "time_off.request_created"
    TIME_OFF_REQUEST_NOT_FOUND = "time_off.request_not_found"
    TIME_OFF_REQUEST_ALREADY_PROCESSED = "time_off.request_already_processed"
    TIME_OFF_REQUEST_APPROVED = "time_off.request_approved"
    TIME_OFF_REQUEST_REJECTED = "time_off.request_rejected"
    TIME_OFF_PARSE_ERROR = "time_off.parse_error"
    TIME_OFF_UNKNOWN_INTENT = "time_off.unknown_intent"
    TIME_OFF_NO_PENDING_REQUESTS = "time_off.no_pending_requests"
    TIME_OFF_PENDING_REQUESTS_TITLE = "time_off.pending_requests_title"


