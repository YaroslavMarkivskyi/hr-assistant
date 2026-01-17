from typing import Optional, List
from datetime import date
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from .models import LeaveRequestModel, EmployeeModel, TimeOffSettingsModel
from .schemas import LeaveRequest, TimeOffSettings, EmployeeBalance
from .enums import LeaveRequestStatus

class TimeOffRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_settings(self, company_id: str = "default") -> TimeOffSettings:
        stmt = select(TimeOffSettingsModel).where(TimeOffSettingsModel.company_id == company_id)
        obj = self.session.scalar(stmt)
        
        if not obj:
            obj = TimeOffSettingsModel(company_id=company_id)
            self.session.add(obj)
            self.session.commit()        
        return TimeOffSettings.model_validate(obj, from_attributes=True)

    def get_employee_balance(self, aad_id: str) -> Optional[EmployeeBalance]:
        stmt = select(EmployeeModel).where(EmployeeModel.aad_id == aad_id)
        emp = self.session.scalar(stmt)
        
        if not emp:
            return None
            
        return EmployeeBalance(
            user_aad_id=emp.aad_id,
            vacation_balance=emp.vacation_balance,
            sick_leave_balance=emp.sick_balance,
            days_off_balance=emp.days_off_balance,
            year=date.today().year 
        )

    def create_request(self, schema: LeaveRequest) -> LeaveRequest:
        emp = self.session.scalar(select(EmployeeModel).where(EmployeeModel.aad_id == schema.user_aad_id))
        if not emp:
            raise ValueError(f"User {schema.user_aad_id} not found")

        data = schema.model_dump(exclude={"id", "created_at", "updated_at"})
        
        db_model = LeaveRequestModel(
            **data,
            employee_id=emp.id
        )
        
        self.session.add(db_model)
        self.session.commit()
        self.session.refresh(db_model)
        
        return LeaveRequest.model_validate(db_model, from_attributes=True)

    def get_user_requests(self, aad_id: str, status: Optional[LeaveRequestStatus] = None) -> List[LeaveRequest]:
        query = select(LeaveRequestModel).where(LeaveRequestModel.user_aad_id == aad_id)
        
        if status:
            query = query.where(LeaveRequestModel.status == status)
            
        query = query.order_by(LeaveRequestModel.created_at.desc())
        
        results = self.session.scalars(query).all()
        
        return [LeaveRequest.model_validate(r, from_attributes=True) for r in results]
    
    