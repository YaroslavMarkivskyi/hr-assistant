from typing import Optional

from pydantic import BaseModel


class Participant(BaseModel):
    """Participant in a meeting or scheduling operation"""
    id: Optional[str] = None  # Azure AD Object ID
    displayName: Optional[str] = None  # Full display name
    mail: Optional[str] = None  # Email address
    userPrincipalName: Optional[str] = None  # UPN (user@domain.com)
    givenName: Optional[str] = None  # First name
    surname: Optional[str] = None  # Last name
    email: Optional[str] = None  # Alias for mail or userPrincipalName
    
    def get_email(self) -> Optional[str]:
        """Get email address (mail, userPrincipalName, or email field)"""
        return self.mail or self.userPrincipalName or self.email
    
    def get_display_name(self) -> str:
        """Get display name or fallback to email"""
        return self.displayName or self.get_email() or "Unknown"


__all__ = (
    "Participant",
    )

