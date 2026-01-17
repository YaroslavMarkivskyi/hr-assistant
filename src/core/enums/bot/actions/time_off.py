from enum import StrEnum


class TimeOffAction(StrEnum):
    """Actions related to Time Off Module"""
    SUBMIT_REQUEST = "submit_timeoff_request"
    CANCEL_MY_REQUEST = "cancel_my_timeoff_request"

__all__ = ("TimeOffAction",)

