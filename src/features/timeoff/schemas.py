from __future__ import annotations
from typing import Optional, List, Union, Any
from datetime import datetime, date, timezone
from pydantic import BaseModel, Field, computed_field, model_validator, ConfigDict, field_validator

from .enums import LeaveType, LeaveRequestStatus


class TimeOffSettings(BaseModel):
    company_id: str = Field(
        default="default",
        description="Unique identifier for the company.",
    )
    vacation_limit: int = Field(
        default=20,
        ge=0,
        description="Annual vacation days limit.",
    )
    sick_leave_limit: int = Field(
        default=10,
        ge=0,
        description="Annual sick leave days limit.",
    )
    carry_over_limit: int = Field(
        default=5,
        ge=0,
        description="Maximum number of vacation days that can be carried over to the next year.",
    )
    days_off_limit: int = Field(
        default=5,
        ge=0,
        description="Annual days off limit.",
    )
    

class LeaveRequest(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the leave request.",
    )
    user_aad_id: str = Field(
        ...,
        description="Azure Active Directory ID of the user requesting leave.",
    )
    approver_aad_id: Optional[str] = Field(
        default=None,
        description="Azure AD ID of the manager who approved/rejected the request.",
    )
    leave_type: LeaveType = Field(
        ...,
        description="Type of leave requested.",
    )
    start_date: date = Field(
        ...,
        description="Start date of the leave.",
    )
    end_date: date = Field(
        ...,
        description="End date of the leave.",
    )
    days_count: int = Field(
        ...,
        ge=1,
        description="Total number of days requested for leave.",
    )
    status: LeaveRequestStatus = Field(
        default=LeaveRequestStatus.PENDING,
        description="Current status of the leave request.",
    )
    reason: Optional[str] = Field(
        default=None,
        description="Optional reason provided by the user for the leave request.",
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        description="Reason for rejection if the leave request was denied.",
    )
    approver_note: Optional[str] = Field(
        default=None,
        description="Optional note from the approver regarding the leave request.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the leave request was created.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the leave request was last updated.",
    )
    
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def is_past_request(self) -> bool:
        """Determine if the leave request is for past dates."""
        return self.end_date < date.today()
    
    @model_validator(mode="after")
    def validate_dates(self) -> LeaveRequest:
        """Ensure that the end date is not before the start date."""
        if self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date.")
        return self
    

class EmployeeBalance(BaseModel):
    user_aad_id: str = Field(
        ...,
        description="Azure Active Directory ID of the employee.",
    )
    vacation_balance: int = Field(
        default=0,
        ge=0,
        description="Remaining vacation days balance.",
    )
    sick_leave_balance: int = Field(
        default=0,
        ge=0,
        description="Remaining sick leave days balance.",
    )
    days_off_balance: int = Field(
        default=0,
        ge=0,
        description="Remaining days off balance.",
    )
    year: int = Field(
        default=datetime.now().year,
        description="Year for which the balances are applicable.",
    )
    

class TimeOffResult(BaseModel):
    success: bool = Field(
        ...,
        description="Indicates if the operation was successful.",
    )
    message: Optional[str] = Field(
        default=None,
        description="Optional message providing additional information about the operation result.",
    )
    data: Optional[Union[List[LeaveRequest], LeaveRequest, EmployeeBalance, dict]] = Field(
        default=None,
        description="Optional list of leave requests related to the operation.",
    )
    

class TimeOffExtractionParams(BaseModel):
    leave_type: Optional[LeaveType] = Field(
        default=None,
        description="Extracted type of leave (vacation, sick, day_off).",
    )
    start_date: Optional[date] = Field(
        default=None,
        description="Extracted start date of the leave.",
    )
    end_date: Optional[date] = Field(
        default=None,
        description="Extracted end date of the leave.",
    )
    reason: Optional[str] = Field(
        default=None,
        description="Extracted reason for the leave request.",
    )
    
    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> Optional[date]:
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.split("T")[0]).date()
            except ValueError:
                raise ValueError(f"Invalid date string: {v}")
        return v
    
class LeaveRequestFormViewModel(BaseModel):
    default_type: Optional[LeaveType] = Field(
        default=None,
        description="Pre-filled leave type for the request form.",
    )
    default_start_date: Optional[str] = Field(
        default=None,
        description="Pre-filled start date (ISO string) for the request form.",
    )
    default_end_date: Optional[str] = Field(
        default=None,
        description="Pre-filled end date (ISO string) for the request form.",
    )
    default_reason: Optional[str] = Field(
        default=None,
        description="Pre-filled reason for the request form.",
    )
    

class BalanceViewModel(BaseModel):
    vacation_total: int = Field(
        ...,
        description="Total vacation days allocated for the year.",
    )
    vacation_available: int = Field(
        ...,
        description="Available vacation days remaining.",
    )
    sick_total: int = Field(
        ...,
        description="Total sick leave days allocated for the year.",
    )
    sick_available: int = Field(
        ...,
        description="Available sick leave days remaining.",
    )
    days_off_total: int = Field(
        ...,
        description="Total days off allocated for the year.",
    )
    days_off_used: int = Field(
        ...,
        description="Days off already used.",
    )
    year: int = Field(
        ...,
        description="Year for which the balance is applicable.",
    )
    
    
class SubmitLeaveActionPayload(BaseModel):
    leave_type: LeaveType = Field(
        ...,
        description="Type of leave requested.",
    )
    start_date: date = Field(
        ...,
        description="Start date of the leave.",
    )
    end_date: date = Field(
        ...,
        description="End date of the leave.",
    )
    reason: Optional[str] = Field(
        default=None,
        description="Optional reason provided by the user for the leave request.",
    )
    
    
__all__ = [
    "TimeOffSettings",
    "LeaveRequest",
    "EmployeeBalance",
    "TimeOffResult",
    "LeaveRequestFormViewModel",
    "TimeOffExtractionParams",
    "BalanceViewModel",
    "SubmitLeaveActionPayload",
]
