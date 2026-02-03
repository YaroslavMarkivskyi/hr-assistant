"""
Database service for managing employees and leave requests using SQLAlchemy ORM.
Updated for SQLAlchemy 2.0 and new Schema while keeping legacy methods support.
"""
from sqlalchemy import create_engine, and_, or_, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import datetime

from models.employee import Employee
from models.leave_request import LeaveRequest, LeaveType, LeaveStatus

from db.base import Base

from db.models import EmployeeModel
from features.time_off.models import LeaveRequestModel, TimeOffSettingsModel

from features.time_off.enums import LeaveType as DbLeaveType, LeaveRequestStatus as DbLeaveRequestStatus

class DatabaseService:
    """
    Database service for time off management.
    Acts as an adapter between Legacy Pydantic models and New DB Structure.
    """
    
    def __init__(self, db_path: str = "time_off.db", config=None):
        # Support for config object if passed (for PostgreSQL later)
        if config and hasattr(config, "DATABASE_URL"):
            db_url = config.DATABASE_URL
        else:
            db_url = f"sqlite:///{db_path}"

        self.engine = create_engine(
            db_url,
            echo=True,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
        )
        
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        
        # Initialize tables
        Base.metadata.create_all(bind=self.engine)
    
    def _get_session(self) -> Session:
        return self.SessionLocal()
        
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    # --- Employee methods ---

    def get_employee(self, aad_id: str) -> Optional[Employee]:
        session = self._get_session()
        try:
            stmt = select(EmployeeModel).where(EmployeeModel.aad_id == aad_id)
            db_employee = session.execute(stmt).scalar_one_or_none()
            
            if db_employee:
                print(f"📋 Found employee in DB: {db_employee.aad_id} ({db_employee.full_name})")
                return self._db_to_employee(db_employee)
            
            print(f"📋 Employee not found in DB for AAD ID: {aad_id}")
            return None
        finally:
            session.close()
    
    def create_employee(self, employee: Employee) -> Employee:
        session = self._get_session()
        try:
            stmt = select(EmployeeModel).where(EmployeeModel.aad_id == employee.aad_id)
            db_employee = session.execute(stmt).scalar_one_or_none()
            
            if db_employee:
                # Update existing
                print(f"Updating existing employee: {employee.aad_id}")
                db_employee.full_name = employee.full_name
                db_employee.email = employee.email
                db_employee.manager_aad_id = employee.manager_aad_id
                db_employee.vacation_balance = employee.vacation_balance
                db_employee.sick_balance = employee.sick_balance
            else:
                # Create new
                print(f"Creating new employee in DB: {employee.aad_id}")
                db_employee = EmployeeModel(
                    aad_id=employee.aad_id,
                    full_name=employee.full_name,
                    email=employee.email,
                    manager_aad_id=employee.manager_aad_id,
                    vacation_balance=employee.vacation_balance,
                    sick_balance=employee.sick_balance,
                    days_off_balance=0 
                )
                session.add(db_employee)
            
            session.commit()
            session.refresh(db_employee)
            
            employee.id = db_employee.id
            return employee
        except IntegrityError:
            session.rollback()
            raise
        finally:
            session.close()
    
    def update_employee_balance(self, aad_id: str, vacation_delta: int = 0, sick_delta: int = 0):
        session = self._get_session()
        try:
            stmt = select(EmployeeModel).where(EmployeeModel.aad_id == aad_id)
            db_employee = session.execute(stmt).scalar_one_or_none()
            
            if db_employee:
                db_employee.vacation_balance += vacation_delta
                db_employee.sick_balance += sick_delta
                
                if db_employee.vacation_balance < 0: db_employee.vacation_balance = 0
                if db_employee.sick_balance < 0: db_employee.sick_balance = 0
                
                session.commit()
        finally:
            session.close()
    
    def create_leave_request(self, request: LeaveRequest) -> LeaveRequest:
        session = self._get_session()
        try:
            stmt = select(EmployeeModel).where(EmployeeModel.aad_id == request.user_aad_id)
            employee_record = session.execute(stmt).scalar_one_or_none()
            
            if not employee_record:
                raise ValueError(f"User with AAD ID {request.user_aad_id} not found in DB.")

            try:
                db_leave_type = DbLeaveType(request.leave_type.value)
                db_status = DbLeaveRequestStatus(request.status.value)
            except ValueError:
                # Fallback
                db_leave_type = DbLeaveType.VACATION 
                db_status = DbLeaveRequestStatus.PENDING

            db_request = LeaveRequestModel(
                employee_id=employee_record.id,
                user_aad_id=request.user_aad_id,
                leave_type=db_leave_type,
                start_date=request.start_date,
                end_date=request.end_date,
                days_count=request.days_count,
                status=db_status,
                approver_note=request.approver_note,
            )
            
            session.add(db_request)
            session.commit()
            session.refresh(db_request)
            
            request.id = db_request.id
            return request
        except IntegrityError as e:
            session.rollback()
            print(f"Integrity Error: {e}")
            raise
        finally:
            session.close()
    
    def get_leave_request(self, request_id: int) -> Optional[LeaveRequest]:
        session = self._get_session()
        try:
            db_request = session.get(LeaveRequestModel, request_id)
            if db_request:
                return self._db_to_leave_request(db_request)
            return None
        finally:
            session.close()
    
    def get_pending_requests_for_manager(self, manager_aad_id: str) -> List[LeaveRequest]:
        session = self._get_session()
        try:
            stmt = select(LeaveRequestModel).join(LeaveRequestModel.employee).where(
                and_(
                    EmployeeModel.manager_aad_id == manager_aad_id,
                    LeaveRequestModel.status == DbLeaveRequestStatus.PENDING
                )
            ).order_by(LeaveRequestModel.created_at.desc())
            
            db_requests = session.execute(stmt).scalars().all()
            return [self._db_to_leave_request(req) for req in db_requests]
        finally:
            session.close()
    
    def get_user_requests(self, user_aad_id: str, status: Optional[LeaveStatus] = None) -> List[LeaveRequest]:
        session = self._get_session()
        try:
            query = select(LeaveRequestModel).where(LeaveRequestModel.user_aad_id == user_aad_id)
            
            if status:
                try:
                    target_status = DbLeaveRequestStatus(status.value)
                    query = query.where(LeaveRequestModel.status == target_status)
                except ValueError:
                    pass 
            
            query = query.order_by(LeaveRequestModel.created_at.desc())
            db_requests = session.execute(query).scalars().all()
            
            return [self._db_to_leave_request(req) for req in db_requests]
        finally:
            session.close()
    
    def update_leave_request_status(self, request_id: int, status: LeaveStatus, approver_note: Optional[str] = None) -> bool:
        session = self._get_session()
        try:
            db_request = session.get(LeaveRequestModel, request_id)
            if db_request:
                # Convert Pydantic Enum -> DB Enum
                db_request.status = DbLeaveRequestStatus(status.value)
                db_request.approver_note = approver_note
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def check_date_overlap(self, user_aad_id: str, start_date: datetime, end_date: datetime, exclude_request_id: Optional[int] = None) -> bool:
        session = self._get_session()
        try:
            s_date = start_date.date() if isinstance(start_date, datetime) else start_date
            e_date = end_date.date() if isinstance(end_date, datetime) else end_date

            stmt = select(LeaveRequestModel).where(
                and_(
                    LeaveRequestModel.user_aad_id == user_aad_id,
                    LeaveRequestModel.status == DbLeaveRequestStatus.APPROVED
                )
            )
            
            if exclude_request_id:
                stmt = stmt.where(LeaveRequestModel.id != exclude_request_id)
            
            stmt = stmt.where(
                or_(
                    and_(LeaveRequestModel.start_date <= s_date, LeaveRequestModel.end_date >= s_date),
                    and_(LeaveRequestModel.start_date <= e_date, LeaveRequestModel.end_date >= e_date),
                    and_(LeaveRequestModel.start_date >= s_date, LeaveRequestModel.end_date <= e_date)
                )
            )
            
            overlapping = session.execute(stmt).scalar_one_or_none()
            return overlapping is not None
        finally:
            session.close()
        
    def _db_to_employee(self, db_employee: EmployeeModel) -> Employee:
        return Employee(
            id=db_employee.id,
            aad_id=db_employee.aad_id,
            full_name=db_employee.full_name,
            email=db_employee.email,
            manager_aad_id=db_employee.manager_aad_id,
            vacation_balance=db_employee.vacation_balance,
            sick_balance=db_employee.sick_balance
        )
    
    def _db_to_leave_request(self, db_request: LeaveRequestModel) -> LeaveRequest:
        # DB Enum -> Pydantic Enum
        return LeaveRequest(
            id=db_request.id,
            user_aad_id=db_request.user_aad_id,
            leave_type=LeaveType(db_request.leave_type.value), 
            start_date=db_request.start_date,
            end_date=db_request.end_date,
            days_count=db_request.days_count,
            status=LeaveStatus(db_request.status.value),
            approver_note=db_request.approver_note,
            created_at=db_request.created_at
        )