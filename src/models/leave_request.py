"""
Leave request model using Pydantic
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional
from enum import Enum


class LeaveType(str, Enum):
    """Types of leave requests"""
    VACATION = "vacation"
    SICK_LEAVE = "sick_leave"
    UNPAID = "unpaid"
    DAY_OFF = "day_off"


class LeaveStatus(str, Enum):
    """Status of leave request"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"


class LeaveRequest(BaseModel):
    """
    Leave request model with validation
    """
    id: Optional[int] = None
    user_aad_id: str = Field(..., description="User's Azure Active Directory ID")
    leave_type: LeaveType = Field(..., description="Type of leave request")
    start_date: datetime = Field(..., description="Start date of leave")
    end_date: datetime = Field(..., description="End date of leave")
    days_count: int = Field(..., gt=0, description="Number of days")
    status: LeaveStatus = Field(default=LeaveStatus.PENDING, description="Request status")
    approver_note: Optional[str] = Field(None, description="Note from approver")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Validate that end date is not earlier than start date"""
        if self.end_date < self.start_date:
            raise ValueError("End date cannot be earlier than start date")
        return self
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_aad_id": "123e4567-e89b-12d3-a456-426614174000",
                "leave_type": "vacation",
                "start_date": "2024-05-20T00:00:00",
                "end_date": "2024-05-25T00:00:00",
                "days_count": 5,
                "status": "PENDING",
                "approver_note": None,
                "created_at": "2024-05-15T10:00:00"
            }
        }
