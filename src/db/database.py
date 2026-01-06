"""
Database service for managing employees and leave requests using SQLAlchemy ORM
"""
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import datetime

from models.employee import Employee
from models.leave_request import LeaveRequest, LeaveType, LeaveStatus
from db.models import Base, EmployeeModel, LeaveRequestModel


class DatabaseService:
    """
    Database service for time off management
    Uses SQLAlchemy ORM with SQLite for MVP, can be migrated to PostgreSQL later
    """
    
    def __init__(self, db_path: str = "time_off.db"):
        """
        Initialize database service
        
        Args:
            db_path: Path to SQLite database file
        """
        # Create engine with SQLite
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,  # Set to True for SQL debugging
            connect_args={"check_same_thread": False}  # SQLite specific
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def _get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    # Employee methods
    def get_employee(self, aad_id: str) -> Optional[Employee]:
        """
        Get employee by AAD ID (Azure AD Object ID)
        
        Args:
            aad_id: Azure AD Object ID (from ctx.activity.from_property.aad_object_id or TEST_USER_ID)
            
        Returns:
            Employee model if found, None otherwise
        """
        session = self._get_session()
        try:
            db_employee = session.query(EmployeeModel).filter(EmployeeModel.aad_id == aad_id).first()
            if db_employee:
                print(f"📋 Found employee in DB: {db_employee.aad_id} ({db_employee.full_name})")
                return self._db_to_employee(db_employee)
            print(f"📋 Employee not found in DB for AAD ID: {aad_id}")
            return None
        finally:
            session.close()
    
    def create_employee(self, employee: Employee) -> Employee:
        """
        Create or update employee in database
        
        Args:
            employee: Employee model with aad_id (Azure AD Object ID)
            
        Returns:
            Employee with database ID set
            
        Note:
            - aad_id is the Azure AD Object ID (unique identifier from Azure)
            - For local testing, TEST_USER_ID is used as aad_id
            - If Graph API is available, full_name and email are fetched from Azure
            - If Graph API is unavailable, default values are used
        """
        session = self._get_session()
        try:
            # Check if employee exists
            db_employee = session.query(EmployeeModel).filter(EmployeeModel.aad_id == employee.aad_id).first()
            
            if db_employee:
                # Update existing
                print(f"🔄 Updating existing employee: {employee.aad_id}")
                db_employee.full_name = employee.full_name
                db_employee.email = employee.email
                db_employee.manager_aad_id = employee.manager_aad_id
                db_employee.vacation_balance = employee.vacation_balance
                db_employee.sick_balance = employee.sick_balance
            else:
                # Create new
                print(f"➕ Creating new employee in DB:")
                print(f"   AAD ID: {employee.aad_id}")
                print(f"   Name: {employee.full_name}")
                print(f"   Email: {employee.email}")
                print(f"   Manager AAD ID: {employee.manager_aad_id}")
                print(f"   Vacation Balance: {employee.vacation_balance}")
                print(f"   Sick Balance: {employee.sick_balance}")
                db_employee = EmployeeModel(
                    aad_id=employee.aad_id,
                    full_name=employee.full_name,
                    email=employee.email,
                    manager_aad_id=employee.manager_aad_id,
                    vacation_balance=employee.vacation_balance,
                    sick_balance=employee.sick_balance
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
        """Update employee balance (for approved/rejected requests)"""
        session = self._get_session()
        try:
            db_employee = session.query(EmployeeModel).filter(EmployeeModel.aad_id == aad_id).first()
            if db_employee:
                db_employee.vacation_balance += vacation_delta
                db_employee.sick_balance += sick_delta
                
                # Ensure balances don't go negative
                if db_employee.vacation_balance < 0:
                    db_employee.vacation_balance = 0
                if db_employee.sick_balance < 0:
                    db_employee.sick_balance = 0
                
                session.commit()
        finally:
            session.close()
    
    # Leave request methods
    def create_leave_request(self, request: LeaveRequest) -> LeaveRequest:
        """Create leave request"""
        session = self._get_session()
        try:
            db_request = LeaveRequestModel(
                user_aad_id=request.user_aad_id,
                leave_type=request.leave_type.value,  # Store enum value as string
                start_date=request.start_date,
                end_date=request.end_date,
                days_count=request.days_count,
                status=request.status.value,  # Store enum value as string
                approver_note=request.approver_note,
                created_at=request.created_at
            )
            
            session.add(db_request)
            session.commit()
            session.refresh(db_request)
            
            request.id = db_request.id
            return request
        except IntegrityError:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_leave_request(self, request_id: int) -> Optional[LeaveRequest]:
        """Get leave request by ID"""
        session = self._get_session()
        try:
            db_request = session.query(LeaveRequestModel).filter(LeaveRequestModel.id == request_id).first()
            if db_request:
                return self._db_to_leave_request(db_request)
            return None
        finally:
            session.close()
    
    def get_pending_requests_for_manager(self, manager_aad_id: str) -> List[LeaveRequest]:
        """Get all pending requests for a manager"""
        session = self._get_session()
        try:
            db_requests = session.query(LeaveRequestModel).join(
                EmployeeModel,
                LeaveRequestModel.user_aad_id == EmployeeModel.aad_id
            ).filter(
                and_(
                    EmployeeModel.manager_aad_id == manager_aad_id,
                    LeaveRequestModel.status == LeaveStatus.PENDING
                )
            ).order_by(LeaveRequestModel.created_at.desc()).all()
            
            return [self._db_to_leave_request(req) for req in db_requests]
        finally:
            session.close()
    
    def get_user_requests(self, user_aad_id: str, status: Optional[LeaveStatus] = None) -> List[LeaveRequest]:
        """Get all requests for a user"""
        session = self._get_session()
        try:
            query = session.query(LeaveRequestModel).filter(
                LeaveRequestModel.user_aad_id == user_aad_id
            )
            
            if status:
                query = query.filter(LeaveRequestModel.status == status)
            
            db_requests = query.order_by(LeaveRequestModel.created_at.desc()).all()
            
            return [self._db_to_leave_request(req) for req in db_requests]
        finally:
            session.close()
    
    def update_leave_request_status(
        self, 
        request_id: int, 
        status: LeaveStatus, 
        approver_note: Optional[str] = None
    ) -> bool:
        """Update leave request status"""
        session = self._get_session()
        try:
            db_request = session.query(LeaveRequestModel).filter(LeaveRequestModel.id == request_id).first()
            if db_request:
                db_request.status = status.value  # Store enum value as string
                db_request.approver_note = approver_note
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def check_date_overlap(self, user_aad_id: str, start_date: datetime, end_date: datetime, exclude_request_id: Optional[int] = None) -> bool:
        """Check if dates overlap with existing approved requests"""
        session = self._get_session()
        try:
            query = session.query(LeaveRequestModel).filter(
                and_(
                    LeaveRequestModel.user_aad_id == user_aad_id,
                    LeaveRequestModel.status == LeaveStatus.APPROVED.value  # Compare with enum value
                )
            )
            
            if exclude_request_id:
                query = query.filter(LeaveRequestModel.id != exclude_request_id)
            
            # Check for date overlap
            # Overlap occurs if:
            # - New start is between existing start and end
            # - New end is between existing start and end
            # - New range completely contains existing range
            overlapping = query.filter(
                or_(
                    and_(
                        LeaveRequestModel.start_date <= start_date,
                        LeaveRequestModel.end_date >= start_date
                    ),
                    and_(
                        LeaveRequestModel.start_date <= end_date,
                        LeaveRequestModel.end_date >= end_date
                    ),
                    and_(
                        LeaveRequestModel.start_date >= start_date,
                        LeaveRequestModel.end_date <= end_date
                    )
                )
            ).first()
            
            return overlapping is not None
        finally:
            session.close()
    
    # Conversion methods
    def _db_to_employee(self, db_employee: EmployeeModel) -> Employee:
        """Convert SQLAlchemy model to Employee"""
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
        """Convert SQLAlchemy model to LeaveRequest"""
        return LeaveRequest(
            id=db_request.id,
            user_aad_id=db_request.user_aad_id,
            leave_type=LeaveType(db_request.leave_type),  # Convert string back to enum
            start_date=db_request.start_date,
            end_date=db_request.end_date,
            days_count=db_request.days_count,
            status=LeaveStatus(db_request.status),  # Convert string back to enum
            approver_note=db_request.approver_note,
            created_at=db_request.created_at
        )
