"""
Helper functions for extracting user information from Teams context
"""
from microsoft.teams.apps import ActivityContext
from config import Config


def get_user_aad_id(ctx: ActivityContext, config: Config) -> str | None:
    """
    Extracts user AAD ID (Azure AD Object ID) from Teams activity context.
    Falls back to TEST_USER_ID for local testing if not found.
    
    This ID is used as the primary key (aad_id) in the employees table.
    
    Args:
        ctx: Activity context from Teams
        config: Application configuration
        
    Returns:
        User's Azure AD Object ID (GUID format), or TEST_USER_ID for local testing, or None
        
    Example:
        In production: "123e4567-e89b-12d3-a456-426614174000" (from Teams)
        In local testing: value from TEST_USER_ID env variable
    """
    aad_id = None
    
    # Try to get from activity context
    if hasattr(ctx.activity, 'from_property') and ctx.activity.from_property:
        # Priority 1: aad_object_id (Azure AD Object ID - this is what we need)
        # This is a GUID like "123e4567-e89b-12d3-a456-426614174000"
        aad_id = getattr(ctx.activity.from_property, 'aad_object_id', None)
        
        if aad_id:
            print(f"✅ Found AAD Object ID from Teams: {aad_id}")
        
        # Priority 2: id (fallback, might be different format)
        if not aad_id:
            aad_id = getattr(ctx.activity.from_property, 'id', None)
            if aad_id:
                print(f"⚠️ Using 'id' instead of 'aad_object_id': {aad_id}")
    
    # For local testing: use test ID if not found
    if not aad_id and config.TEST_USER_ID:
        aad_id = config.TEST_USER_ID
        print(f"🧪 Using TEST_USER_ID for local testing: {aad_id}")
        print(f"   This can be ANY string - doesn't need to be a real Azure AD Object ID")
        print(f"   This will be stored as 'aad_id' in the database")
    elif not aad_id:
        print("⚠️ User AAD ID not found in activity context and TEST_USER_ID not set.")
        print("   Set TEST_USER_ID in .env for local testing, or ensure Teams provides aad_object_id")
        print("   Example: TEST_USER_ID=123e4567-e89b-12d3-a456-426614174000")
        print("   Or even: TEST_USER_ID=test-user-123 (any string works for testing)")
    
    return aad_id
