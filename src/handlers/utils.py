"""
Shared utilities for handlers
"""
import logging
from typing import Optional
from bot.activity_context_wrapper import ActivityContextWrapper

logger = logging.getLogger("HRBot")


def get_requester_id(ctx: ActivityContextWrapper, config) -> Optional[str]:
    """
    Extracts requester ID from activity context with clear priority order.
    
    Priority order (most to least preferred):
    1. AAD Object ID (aad_object_id) - Global corporate ID for Azure AD integration
       Used for: vacation checks, calendar access, manager lookup
    2. Channel Account ID (id) - Technical ID for bot channel communication
       Used for: replying to messages (ReplyToId), not for business logic
    3. Test User ID (TEST_USER_ID) - Fallback for local development/testing
    
    Args:
        ctx: Activity context wrapper (adapts TurnContext to ActivityContext API)
        config: Application configuration with optional TEST_USER_ID
        
    Returns:
        Requester ID (AAD object ID, channel ID, or test ID) or None if not found
        
    Note:
        In Bot Framework SDK, Activity structure is well-defined:
        - ctx.activity.from_property contains user information
        - from_property.aad_object_id is the Azure AD Object ID (GUID)
        - from_property.id is the Channel Account ID (may vary per channel)
    """
    # Get activity from context (ActivityContextWrapper always has .activity)
    activity = getattr(ctx, 'activity', None)
    if not activity:
        logger.warning("⚠️ Activity not found in context")
        return _get_test_user_id(config)
    
    # Get from_property (ChannelAccount object with user info)
    from_property = getattr(activity, 'from_property', None)
    if not from_property:
        logger.warning("⚠️ from_property not found in activity")
        return _get_test_user_id(config)
    
    # Priority 1: AAD Object ID (Azure AD Object ID - preferred for business logic)
    # This is a GUID like "123e4567-e89b-12d3-a456-426614174000"
    # Used for: vacation checks, calendar access, manager lookup, database queries
    aad_object_id = getattr(from_property, 'aad_object_id', None)
    if aad_object_id:
        logger.debug(f"✅ Found AAD Object ID: {aad_object_id}")
        return aad_object_id
    
    # Priority 2: Channel Account ID (fallback - technical ID for channel communication)
    # This ID may change if bot is reinstalled or channel changes
    # Used for: replying to messages (ReplyToId), not for business logic
    channel_id = getattr(from_property, 'id', None)
    if channel_id:
        logger.warning(f"⚠️ Using Channel Account ID instead of AAD Object ID: {channel_id}")
        return channel_id
    
    # Priority 3: Test User ID (fallback for local development)
    logger.warning("⚠️ No user ID found in activity. Falling back to test ID if configured.")
    return _get_test_user_id(config)


def _get_test_user_id(config) -> Optional[str]:
    """
    Gets test user ID from config for local development.
    
    Args:
        config: Application configuration
        
    Returns:
        Test user ID if configured, None otherwise
    """
    test_user_id = getattr(config, 'TEST_USER_ID', None)
    if test_user_id:
        logger.info(f"🧪 Using test requester_id: {test_user_id}")
        return test_user_id
    
    logger.warning("⚠️ Requester ID not found. User will not be added as participant automatically.")
    return None

