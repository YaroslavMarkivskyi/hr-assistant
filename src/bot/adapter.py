"""
Bot Framework Adapter Configuration

Handles all Azure Bot Framework adapter setup, including Single Tenant configuration.
Isolates authentication and connection logic from business logic.
"""
import sys
import logging
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botframework.connector.auth import AuthenticationConfiguration
from core.config import settings

logger = logging.getLogger("HRBot")


def _clean_config_value(value: str) -> str:
    """Clean configuration value from quotes and whitespace"""
    return str(value).strip().strip('"').strip("'")


def create_adapter() -> BotFrameworkAdapter:
    """
    Create and configure BotFrameworkAdapter with Single Tenant support.
    
    This function handles:
    - Configuration value cleaning
    - Authentication setup
    - Single Tenant channel_auth_tenant configuration
    - Error handling setup
    
    Returns:
        Configured BotFrameworkAdapter instance
        
    Raises:
        SystemExit: If adapter initialization fails
    """
    # Clean configuration values
    clean_app_id = _clean_config_value(settings.APP_ID)
    clean_password = _clean_config_value(settings.APP_PASSWORD)
    clean_tenant_id = _clean_config_value(settings.TENANT_ID)
    
    logger.info(f"🔑 BOT_ID: {clean_app_id}")
    logger.info(f"🏢 TENANT_ID: {clean_tenant_id}")
    
    try:
        # Authentication configuration for validating INCOMING tokens
        auth_config = AuthenticationConfiguration(
            claims_validator=None,
            tenant_id=clean_tenant_id
        )
        
        # Adapter settings with Single Tenant fix
        adapter_settings = BotFrameworkAdapterSettings(
            app_id=clean_app_id,
            app_password=clean_password,
            auth_configuration=auth_config,
            # [GITHUB FIX] Critical for Single Tenant!
            # Tells adapter: "When sending messages, request token from THIS tenant"
            channel_auth_tenant=clean_tenant_id
        )
        
        # Create adapter
        adapter = BotFrameworkAdapter(adapter_settings)
        
        # Set up error handler
        async def on_error(context: TurnContext, error: Exception):
            logger.error(f"❌ Bot Error: {error}", exc_info=True)
        
        adapter.on_turn_error = on_error
        
        logger.info("✅ BotFrameworkAdapter initialized with channel_auth_tenant")
        return adapter
        
    except Exception as e:
        logger.error(f"❌ Critical Adapter Init Error: {e}", exc_info=True)
        sys.exit(1)

