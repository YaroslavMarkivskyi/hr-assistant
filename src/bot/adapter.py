import logging
from typing import TYPE_CHECKING

from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)

from botframework.connector.auth import AuthenticationConfiguration


logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from core.config import Config


def create_adapter(config: "Config") -> BotFrameworkAdapter:
    """
    Create and configure BotFrameworkAdapter with Single Tenant support.
    
    This function handles:
    - Configuration value cleaning
    - Authentication setup
    - Single Tenant channel_auth_tenant configuration
    - Error handling setup
    
    Returns:
        Configured BotFrameworkAdapter instance
        
    """
    auth_config = AuthenticationConfiguration(
        tenant_id=config.TENANT_ID
    )
    settings = BotFrameworkAdapterSettings(
        app_id=config.APP_ID,
        app_password=config.APP_PASSWORD,
        auth_configuration=auth_config,
        channel_auth_tenant=config.TENANT_ID  # Critical for Single Tenant!
    )
    
    adapter = BotFrameworkAdapter(settings)
    
    async def on_error(context: TurnContext, error: Exception):
        logger.error(f"Bot Error: {error}", exc_info=True)
        try:
            # TODO: Localize this message
            await context.send_activity("The bot encountered an error or bug.")
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}", exc_info=True)
            # TODO: Clear conversation state if needed
    
    adapter.on_turn_error = on_error
    logger.info("BotFrameworkAdapter initialized with channel_auth_tenant")
    return adapter


__all__ = ("create_adapter",)





# import sys
# import logging
# from typing import TYPE_CHECKING

# from botbuilder.core import (
#     BotFrameworkAdapter,
#     BotFrameworkAdapterSettings,
#     TurnContext,
# )
# from botframework.connector.auth import AuthenticationConfiguration

# logger = logging.getLogger("HRBot")


# if TYPE_CHECKING:
#     from core.config import Config



# def _clean_config_value(value: str) -> str:
#     """Clean configuration value from quotes and whitespace"""
#     return str(value).strip().strip('"').strip("'")


# def create_adapter(config: "Config") -> BotFrameworkAdapter:
#     """
#     Create and configure BotFrameworkAdapter with Single Tenant support.
    
#     This function handles:
#     - Configuration value cleaning
#     - Authentication setup
#     - Single Tenant channel_auth_tenant configuration
#     - Error handling setup
    
#     Returns:
#         Configured BotFrameworkAdapter instance
        
#     Raises:
#         SystemExit: If adapter initialization fails
#     """
#     # Clean configuration values
#     clean_app_id = _clean_config_value(config.APP_ID)
#     clean_password = _clean_config_value(config.APP_PASSWORD)
#     clean_tenant_id = _clean_config_value(config.TENANT_ID)
    
#     logger.info(f"BOT_ID: {clean_app_id}")
#     logger.info(f"TENANT_ID: {clean_tenant_id}")
    
#     try:
#         # Authentication configuration for validating INCOMING tokens
#         auth_config = AuthenticationConfiguration(
#             claims_validator=None,
#             tenant_id=clean_tenant_id
#         )
        
#         # Adapter settings with Single Tenant fix
#         adapter_settings = BotFrameworkAdapterSettings(
#             app_id=clean_app_id,
#             app_password=clean_password,
#             auth_configuration=auth_config,
#             # [GITHUB FIX] Critical for Single Tenant!
#             # Tells adapter: "When sending messages, request token from THIS tenant"
#             channel_auth_tenant=clean_tenant_id
#         )
        
#         # Create adapter
#         adapter = BotFrameworkAdapter(adapter_settings)
        
#         # Set up error handler
#         async def on_error(context: TurnContext, error: Exception):
#             logger.error(f"Bot Error: {error}", exc_info=True)
        
#         adapter.on_turn_error = on_error
        
#         logger.info("BotFrameworkAdapter initialized with channel_auth_tenant")
#         return adapter
        
#     except Exception as e:
#         logger.error(f"Critical Adapter Init Error: {e}", exc_info=True)
#         sys.exit(1)

