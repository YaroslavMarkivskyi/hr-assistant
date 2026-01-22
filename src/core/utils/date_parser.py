import logging
import re
from typing import Optional, Union
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


def parse_date(
    date_input: Union[str, datetime, None],
    reference_date: Optional[datetime] = None
) -> Optional[datetime]:
    if date_input is None:
        return None
    
    if isinstance(date_input, datetime):
        return date_input
    
    if not isinstance(date_input, str):
        return None
    
    if not reference_date:
        reference_date = datetime.now(timezone.utc)
    if reference_date.tzinfo is None:
        reference_date = reference_date.replace(tzinfo=timezone.utc)

    ref_tz = reference_date.tzinfo
    
    date_str = date_input.strip().lower()
    
    # Relative dates
    if date_str in ["tomorrow", "завтра"]:
        return reference_date + timedelta(days=1)
    if date_str in ["today", "сьогодні"]:
        return reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Days of week mapping
    days_uk = {
        "понеділок": 0, "вівторок": 1, "середа": 2, "середу": 2,
        "четвер": 3, "п'ятниця": 4, "субота": 5, "неділя": 6
    }
    days_en = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    
    next_match = re.match(r"(next|наступний|наступну)\s+(\w+)", date_str)
    if next_match:
        day_name = next_match.group(2).lower()
        target_weekday = days_uk.get(day_name) or days_en.get(day_name)
        if target_weekday is not None:
            days_ahead = (target_weekday - reference_date.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7
            return (reference_date + timedelta(days=days_ahead)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
    
    for day_name, weekday in {**days_uk, **days_en}.items():
        if date_str == day_name or date_str.endswith(day_name):
            target_weekday = weekday
            days_ahead = (target_weekday - reference_date.weekday() + 7) % 7
            if days_ahead == 0:  # Today
                return reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
            return (reference_date + timedelta(days=days_ahead)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        if dt.tzinfo is None and ref_tz is not None:
            dt = dt.replace(tzinfo=ref_tz)
        return dt
    except (ValueError, AttributeError):
        pass
    
    # Try other common formats
    formats = [
        "%d.%m.%Y",  # 25.12.2023
        "%d/%m/%Y",  # 25/12/2023
        "%m/%d/%Y",  # 12/25/2023
        "%Y-%m-%d",  # Fallback
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=ref_tz)
        except ValueError:
            continue
    
    # Try other common formats
    formats = [
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=ref_tz)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse date: {date_input}")
    return None

