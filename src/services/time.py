# services/time/service.py
from datetime import datetime
import pytz

class TimeService:
    """
    Service for handling time-related operations.
    Using UTC internally is a best practice.
    """
    def __init__(self):
        # TODO make timezone configurable
        self.default_timezone = pytz.timezone('Europe/Kiev')

    def now(self) -> datetime:
        """Returns current time in default timezone."""
        return datetime.now(self.default_timezone)

    def now_utc(self) -> datetime:
        """Returns current time in UTC."""
        return datetime.now(pytz.utc)