"""
Supported languages for the bot
"""
from enum import StrEnum


class Language(StrEnum):
    """
    Supported languages for localization
    """
    ENGLISH = "en"
    UKRAINIAN = "uk"
    
    @classmethod
    def from_locale(cls, locale: str) -> 'Language':
        """
        Converts Teams locale (e.g., 'en-US', 'uk-UA') to Language enum
        
        Args:
            locale: Locale string from Teams (e.g., 'en-US', 'uk-UA', 'en')
            
        Returns:
            Language enum value, defaults to ENGLISH if locale is not recognized
        """
        if not locale:
            return cls.ENGLISH
        
        locale_lower = locale.lower()
        
        # Check for Ukrainian
        if locale_lower.startswith('uk'):
            return cls.UKRAINIAN
        
        # Default to English for all other locales
        return cls.ENGLISH

