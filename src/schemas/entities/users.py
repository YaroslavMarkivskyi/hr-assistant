from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class UserCreateRequest(BaseModel):
    first_name: str = Field(
        ..., 
        alias="firstName",
        min_length=1,
        description="The first name of the user."
        )
    last_name: str = Field(
        ..., 
        alias="lastName",
        min_length=1,
        description="The last name of the user."
        )
    email_nickname: Optional[str] = Field(
        None, 
        description="Optional custom mail prefix. If not provided, generated from name."
        )
    job_title: Optional[str] = Field(
        None, 
        alias="jobTitle",
        description="The job title of the user."
        )
    department: Optional[str] = Field(
        None, 
        description="The department of the user."
        )
    usage_location: str = Field(
        default="US",
        alias="usageLocation",
        min_length=2,
        max_length=2,
        description="The usage location of the user (ISO 2-letter code)."
    )
    
    model_config = ConfigDict(
        populate_by_name=True
    )
    
    @property
    def effective_nickname_source(self) -> str:
        return self.email_nickname or f"{self.first_name}.{self.last_name}".lower()
    
    
class UserResponse(BaseModel):
    user_id: str = Field(
        ..., 
        alias="userId",
        description="The unique identifier of the user."
        )
    email: EmailStr = Field(
        ..., 
        description="The email address of the user."
        )
    password: str = Field(
        ..., 
        description="The temporary password assigned to the user."
        )
    license_assigned: bool = Field(
        ..., 
        alias="licenseAssigned",
        description="Indicates whether a license has been assigned to the user."
        )
    license_error: Optional[str] = Field(
        None, 
        alias="licenseError",
        description="Error message if license assignment failed."
        )
    
    model_config = ConfigDict(
        populate_by_name=True
    )
    

class UserProvisioningData(BaseModel):
    nickname: str = Field(
        ..., 
        description="The email nickname (mail prefix) for the user."
        )
    upn: str = Field(
        ..., 
        alias="upn",
        description="The User Principal Name (UPN) for the user."
        )
    password: str = Field(
        ..., 
        description="The temporary password for the user."
        )    
    
    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True
    )


class UserSearchResult(BaseModel):
    user_id: str = Field(
        ..., 
        alias="userId",
        description="The unique identifier of the user."
        )
    display_name: Optional[str] = Field(
        None,
        alias="displayName",
        description="The display name of the user."
    )
    email: Optional[EmailStr] = Field(
        None,
        description="The email address of the user."
    )
    upn: Optional[str] = Field(
        None,
        alias="upn",
        description="The User Principal Name (UPN) of the user."
    )
    job_title: Optional[str] = Field(
        None,
        alias="jobTitle",
        description="The job title of the user."
    )
    department: Optional[str] = Field(
        None,
        description="The department of the user."
    )
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )
        
    
__all__ = (
    "UserCreateRequest",
    "UserResponse",
    "UserProvisioningData",
    "UserSearchResult",
)

