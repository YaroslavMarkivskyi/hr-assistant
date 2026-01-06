"""
SQLAlchemy ORM models for database
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from models.leave_request import LeaveType, LeaveStatus

Base = declarative_base()


class EmployeeModel(Base):
    """
    SQLAlchemy model for employees table
    """
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aad_id = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    manager_aad_id = Column(String, nullable=True)
    vacation_balance = Column(Integer, default=20, nullable=False)
    sick_balance = Column(Integer, default=10, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    leave_requests = relationship("LeaveRequestModel", back_populates="employee", cascade="all, delete-orphan")


class LeaveRequestModel(Base):
    """
    SQLAlchemy model for leave_requests table
    Note: Using String for enums since SQLite doesn't support native Enum type
    """
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_aad_id = Column(String, ForeignKey("employees.aad_id"), nullable=False, index=True)
    leave_type = Column(String, nullable=False)  # Store as string, convert to LeaveType enum
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    days_count = Column(Integer, nullable=False)
    status = Column(String, default=LeaveStatus.PENDING.value, nullable=False, index=True)  # Store as string
    approver_note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    employee = relationship("EmployeeModel", back_populates="leave_requests")

