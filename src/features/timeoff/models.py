from __future__ import annotations
from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Date, DateTime, Boolean, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base
from .enums import LeaveType, LeaveRequestStatus


class TimeOffSettingsModel(Base):
    __tablename__ = "time_off_settings"

    company_id: Mapped[str] = mapped_column(String, primary_key=True, default="default")
    vacation_limit: Mapped[int] = mapped_column(Integer, default=24)
    sick_leave_limit: Mapped[int] = mapped_column(Integer, default=10)
    carry_over_limit: Mapped[int] = mapped_column(Integer, default=5)
    days_off_limit: Mapped[int] = mapped_column(Integer, default=5)
    
    raw_policy_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class EmployeeModel(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    aad_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    
    full_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    manager_aad_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    vacation_balance: Mapped[int] = mapped_column(Integer, default=0)
    sick_balance: Mapped[int] = mapped_column(Integer, default=0)
    days_off_balance: Mapped[int] = mapped_column(Integer, default=0)
    last_balance_update: Mapped[date] = mapped_column(Date, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    leave_requests: Mapped[List["LeaveRequestModel"]] = relationship(
        back_populates="employee", 
        cascade="all, delete-orphan"
    )


class LeaveRequestModel(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    
    user_aad_id: Mapped[str] = mapped_column(String, index=True) 
    approver_aad_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    leave_type: Mapped[LeaveType] = mapped_column(Enum(LeaveType))
    
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    days_count: Mapped[int] = mapped_column(Integer)
    
    status: Mapped[LeaveRequestStatus] = mapped_column(Enum(LeaveRequestStatus), default=LeaveRequestStatus.PENDING)
    
    reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    approver_note: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.now(), 
        server_default=func.now()
    )

    employee: Mapped["EmployeeModel"] = relationship(back_populates="leave_requests")