from enum import StrEnum


class LeaveType(StrEnum):
    VACATION = "vacation"
    SICK = "sick"
    DAY_OFF = "day_off"
    UNPAID = "unpaid"


class LeaveRequestStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    

class TimeOffAction(StrEnum):
    SUBMIT_REQUEST = "submit_request"
    VIEW_BALANCE = "view_balance"
    VIEW_REQUESTS = "view_requests"
    CANCEL_REQUEST = "cancel_request"


__all__ = [
    "LeaveType",
    "LeaveRequestStatus",
    "TimeOffAction",
]

