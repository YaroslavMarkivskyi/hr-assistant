"""
Common helper functions
"""
from microsoft.teams.apps import ActivityContext
from core.enums.languages import Language


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
        locale = getattr(ctx.activity.from_property, 'locale', None)
    
    return Language.from_locale(locale or "")

