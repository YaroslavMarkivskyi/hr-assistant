"""
Base Module Controller

Provides common functionality for all module controllers:
- Localized error messages
- User validation (requester_id)
- Common helper methods
"""
import logging
from typing import Optional, TYPE_CHECKING, TypeVar, Generic

from core.enums.translation_key import TranslationKey
from handlers.utils import get_requester_id
from resources import get_translation
from core.utils.helpers import get_user_language

if TYPE_CHECKING:
    from bot.activity_context_wrapper import ActivityContextWrapper
    from core.containers.service_container import ServiceContainer

logger = logging.getLogger("HRBot")


TService = TypeVar("TService")


class BaseModuleController(Generic[TService]):
    """
    Base class for all module controllers.
    
    Provides common functionality:
    - Localized error messages
    - User validation (requester_id)
    - Common helper methods
    """
    def __init__(self, service: TService):
        self._service = service
    
    
    def _get_translation(
        self,
        ctx: "ActivityContextWrapper",
        translation_key: TranslationKey,
        **kwargs
    ) -> str:
        """
        Gets a localized translation for the user's language with optional formatting.
        
        First retrieves the translation template, then formats it with provided variables.
        This approach is safer and doesn't depend on get_translation supporting kwargs.
        
        Args:
            ctx: Activity context wrapper
            translation_key: Translation key for the message
            **kwargs: Variables to format into the translation string (e.g., name="John", email="john@example.com")
            
        Returns:
            Localized message string with formatted variables
            
        Example:
            >>> self._get_translation(ctx, TranslationKey.MESSAGE_GREETING, name="Ivan")
            "Привіт, Ivan!"  # or "Hello, Ivan!" depending on language
        """
        language = get_user_language(ctx)
        
        # First, get the translation template (without formatting)
        template = get_translation(translation_key, language)
        
        # Then, format it if kwargs are provided
        if kwargs:
            try:
                return template.format(**kwargs)
            except KeyError as e:
                logger.warning(
                    f"⚠️ Missing format key {e} in translation '{translation_key.value}'. "
                    f"Returning unformatted template."
                )
                return template
            except Exception as e:
                logger.warning(
                    f"⚠️ Formatting error for translation '{translation_key.value}': {e}. "
                    f"Returning unformatted template."
                )
                return template
        
        return template
    
    async def _send_localized(
        self,
        ctx: "ActivityContextWrapper",
        translation_key: TranslationKey,
        **kwargs
    ) -> None:
        """
        Sends a localized message to the user with optional formatting.
        
        Generic method for sending any localized message (not just errors).
        Use this instead of manually calling get_user_language + get_translation.
        
        Args:
            ctx: Activity context wrapper
            translation_key: Translation key for the message
            **kwargs: Variables to format into the translation string (e.g., name="John", email="john@example.com")
            
        Example:
            >>> await self._send_localized(ctx, TranslationKey.MESSAGE_GREETING, name="Ivan")
            # Sends "Привіт, Ivan!" or "Hello, Ivan!" depending on detected language
        """
        try:
            message = self._get_translation(ctx, translation_key, **kwargs)
            await ctx.send_activity(message)
        except Exception as e:
            logger.error(f"❌ Failed to send localized message: {e}")
    
    async def _send_error(
        self,
        ctx: "ActivityContextWrapper",
        translation_key: TranslationKey,
        **kwargs
    ) -> None:
        """
        Sends a localized error message to the user with optional formatting.
        
        This is a convenience wrapper around _send_localized for semantic clarity.
        
        Args:
            ctx: Activity context wrapper
            translation_key: Translation key for the error message
            **kwargs: Variables to format into the translation string (e.g., error="Database connection failed")
            
        Example:
            >>> await self._send_error(ctx, TranslationKey.MESSAGE_PROCESSING_ERROR, error="Timeout")
            # Sends formatted error message with the error details
        """
        await self._send_localized(ctx, translation_key, **kwargs)
    
    async def _get_requester_id_or_error(
        self,
        ctx: "ActivityContextWrapper",
        container: "ServiceContainer"
    ) -> Optional[str]:
        """
        Gets requester ID or sends error message if not found.
        
        Args:
            ctx: Activity context wrapper
            container: Service container with config
            
        Returns:
            Requester ID if found, None otherwise (error already sent to user)
        """
        requester_id = get_requester_id(ctx, container.config)
        
        if not requester_id:
            logger.warning("⚠️ Cannot get requester ID")
            await self._send_error(ctx, TranslationKey.MESSAGE_USER_IDENTIFICATION_ERROR)
            return None
        
        return requester_id
    
    async def _send_unhandled_request(
        self,
        ctx: "ActivityContextWrapper"
    ) -> None:
        """
        Sends a localized "unhandled request" message to the user.
        
        Args:
            ctx: Activity context wrapper
        """
        await self._send_error(ctx, TranslationKey.MESSAGE_UNHANDLED_REQUEST)

