"""
Type definitions for user search service.

This module contains all type definitions used across the user search package.
"""
from typing import Literal, TypedDict

# Type aliases for better type safety
ConfidenceLevel = Literal["high", "medium", "low"]


class UserDict(TypedDict, total=False):
    """
    TypedDict for user data from Microsoft Graph API.
    
    Using TypedDict provides better type safety and IDE autocomplete.
    Fields marked as total=False are optional.
    """
    id: str  # Azure AD Object ID
    displayName: str  # Full display name
    mail: str  # Email address
    userPrincipalName: str  # UPN (user@domain.com)
    givenName: str  # First name
    surname: str  # Last name


