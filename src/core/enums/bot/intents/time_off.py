from enum import StrEnum


class TimeOffIntent(StrEnum):
    """Time off management module intents"""
    REQUEST_LEAVE = "request_leave"  # Submit a leave request
    CHECK_BALANCE = "check_balance"  # Check leave balances
    VIEW_REQUESTS = "view_requests"  # View status of leave requests
    CANCEL_REQUEST = "cancel_request"  # Cancel a leave request


__all__ = ("TimeOffIntent",)

