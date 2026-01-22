from enum import StrEnum


class TimeOffAction(StrEnum):
    """Actions related to Time Off Module"""
    SUBMIT_REQUEST = "submit_time_off_request"
    CANCEL_MY_REQUEST = "cancel_my_time_off_request"

__all__ = ("TimeOffAction",)

