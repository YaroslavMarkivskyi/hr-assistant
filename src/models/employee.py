"""
Employee model for time off balance tracking using Pydantic
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Employee(BaseModel):
    """
    Employee model for tracking vacation and sick leave balances
    """
    id: Optional[int] = None
    aad_id: str = Field(..., description="Azure Active Directory ID")
    full_name: str = Field(..., min_length=1, description="Full name of the employee")
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', description="Email address")
    manager_aad_id: Optional[str] = Field(None, description="Manager's AAD ID")
    vacation_balance: int = Field(default=20, ge=0, description="Vacation days balance")
    sick_balance: int = Field(default=10, ge=0, description="Sick leave days balance")
    
    @field_validator('vacation_balance', 'sick_balance')
    @classmethod
    def validate_balance(cls, v: int) -> int:
        """Validate that balance is not negative"""
        if v < 0:
            raise ValueError("Balance cannot be negative")
        return v
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "aad_id": "123e4567-e89b-12d3-a456-426614174000",
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "manager_aad_id": "123e4567-e89b-12d3-a456-426614174001",
                "vacation_balance": 20,
                "sick_balance": 10
            }
        }
