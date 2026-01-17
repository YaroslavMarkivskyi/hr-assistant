"""
Timeline Builder - Domain logic for building schedule timelines.

This module contains scheduling-specific logic for building day timelines
with busy/available slots. It knows about TimelineSlot models and scheduling concepts.
"""
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta, timezone

from ..schemas import TimelineSlot

logger = logging.getLogger("HRBot")


class TimelineBuilder:
    """
    Builder for schedule timelines.
    
    Splits a day into time slots and marks them as busy or available
    based on calendar events. Groups consecutive slots with same status.
    """
    
    def __init__(
        self,
        slot_duration_minutes: int = 30,
        work_start_hour: int = 0,
        work_end_hour: int = 24
    ):
        """
        Initialize timeline builder.
        
        Args:
            slot_duration_minutes: Duration of each slot in minutes (default 30)
            work_start_hour: Start of working day in hours (default 0)
            work_end_hour: End of working day in hours (default 24)
        """
        self.slot_duration_minutes = slot_duration_minutes
        self.work_start_hour = work_start_hour
        self.work_end_hour = work_end_hour
    
    def build(
        self,
        events: List[Dict[str, Any]],
        day_start: datetime,
        day_end: datetime
    ) -> List[TimelineSlot]:
        """
        Build a timeline of the day split into slots, filling gaps with "available" status.
        
        Args:
            events: List of calendar events with start/end times
            day_start: Start of the day (00:00) - can be naive or timezone-aware
            day_end: End of the day (23:59:59) - can be naive or timezone-aware
            
        Returns:
            List of TimelineSlot objects covering the entire day (grouped)
        """
        # Normalize day boundaries to naive UTC for consistent comparison
        day_start = self._ensure_naive_utc(day_start)
        day_end = self._ensure_naive_utc(day_end)
        
        if not day_start or not day_end:
            logger.error("Invalid day_start or day_end")
            return []
        
        slots = []
        current_time = day_start
        
        # Create a list of busy periods from events
        busy_periods = self._extract_busy_periods(events)
        
        # Build timeline by iterating through the day in slots
        while current_time < day_end:
            slot_end = current_time + timedelta(minutes=self.slot_duration_minutes)
            if slot_end > day_end:
                slot_end = day_end
            
            # Check if this slot overlaps with any busy period
            slot_status, slot_subject = self._check_slot_status(
                current_time, slot_end, busy_periods
            )
            
            # Format subject with emoji and default text for visual appeal
            formatted_subject = self._format_subject(slot_status, slot_subject)
            
            # Create timeline slot
            time_range = f"{current_time.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}"
            slot = TimelineSlot(
                time_range=time_range,
                status=slot_status,
                subject=formatted_subject,
                start=current_time,
                end=slot_end
            )
            slots.append(slot)
            
            current_time = slot_end
        
        # Group consecutive slots with same status
        return self._group_slots(slots)
    
    def _extract_busy_periods(
        self,
        events: List[Dict[str, Any]]
    ) -> List[Tuple[datetime, datetime, str, str]]:
        """
        Extract busy periods from calendar events.
        
        Args:
            events: List of calendar events with start/end, showAs, sensitivity, subject
            
        Returns:
            List of tuples (start_dt, end_dt, subject, status)
            where status is "busy", "ooo", or "available"
        """
        busy_periods = []
        for event in events:
            start_str = event.get("start", {}).get("dateTime", "")
            end_str = event.get("end", {}).get("dateTime", "")
            if start_str and end_str:
                try:
                    # Parse datetime and normalize to UTC naive (remove timezone)
                    start_dt = self._normalize_datetime(start_str)
                    end_dt = self._normalize_datetime(end_str)
                    
                    if not start_dt or not end_dt:
                        continue
                    
                    # Determine status and subject
                    status, subject = self._determine_event_status(event)
                    
                    busy_periods.append((start_dt, end_dt, subject, status))
                except (ValueError, AttributeError, TypeError) as e:
                    logger.warning(f"Error parsing event: {e}")
                    continue
        
        # Sort busy periods by start time
        busy_periods.sort(key=lambda x: x[0])
        return busy_periods
    
    def _normalize_datetime(self, date_str: str) -> Optional[datetime]:
        """
        Normalize datetime string to UTC naive datetime.
        
        Handles both timezone-aware and naive datetime strings.
        Converts all to UTC naive for consistent comparison.
        
        Args:
            date_str: ISO datetime string (may include timezone)
            
        Returns:
            UTC naive datetime or None if parsing fails
        """
        if not date_str:
            return None
        
        try:
            # Replace 'Z' with '+00:00' for ISO parsing
            normalized_str = date_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(normalized_str)
            
            # Convert to UTC if timezone-aware
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc)
                # Remove timezone info (make naive)
                dt = dt.replace(tzinfo=None)
            
            return dt
        except (ValueError, AttributeError) as e:
            logger.warning(f"Error normalizing datetime '{date_str}': {e}")
            return None
    
    def _determine_event_status(self, event: Dict[str, Any]) -> Tuple[str, str]:
        """
        Determine event status (busy/ooo) and subject based on event properties.
        
        Checks:
        - showAs == "oof" (Out of Office)
        - Keywords in subject: "vacation", "відпустка", "лікарняний", "sick"
        - sensitivity == "private" (hide subject)
        
        Args:
            event: Calendar event dict
            
        Returns:
            Tuple of (status, subject) where status is "busy" or "ooo"
        """
        show_as = event.get("showAs", "").lower()
        sensitivity = event.get("sensitivity", "").lower()
        subject = event.get("subject", "Meeting")
        
        # Check for Out of Office
        is_ooo = False
        
        # Check showAs field
        if show_as == "oof":
            is_ooo = True
        
        # Check subject for vacation/sick leave keywords
        if subject:
            subject_lower = subject.lower()
            ooo_keywords = [
                "vacation", "відпустка", "відпуску", "відпуск",
                "sick", "лікарняний", "лікарняне",
                "out of office", "ooo", "off"
            ]
            if any(keyword in subject_lower for keyword in ooo_keywords):
                is_ooo = True
        
        # Determine status
        status = "ooo" if is_ooo else "busy"
        
        # Handle private events - don't show subject
        if sensitivity == "private":
            subject = "Busy" if status == "busy" else "Out of Office"
        
        return (status, subject)
    
    def _check_slot_status(
        self,
        slot_start: datetime,
        slot_end: datetime,
        busy_periods: List[Tuple[datetime, datetime, str, str]]
    ) -> Tuple[str, str]:
        """
        Check if a time slot overlaps with any busy period.
        
        Args:
            slot_start: Start of the slot (naive UTC datetime)
            slot_end: End of the slot (naive UTC datetime)
            busy_periods: List of (start, end, subject, status) tuples
            
        Returns:
            Tuple of (status, subject) where status is "busy", "ooo", or "available"
        """
        # Ensure slot times are naive UTC (normalize if needed)
        slot_start = self._ensure_naive_utc(slot_start)
        slot_end = self._ensure_naive_utc(slot_end)
        
        for busy_start, busy_end, subject, period_status in busy_periods:
            # Ensure busy period times are naive UTC
            busy_start = self._ensure_naive_utc(busy_start)
            busy_end = self._ensure_naive_utc(busy_end)
            
            # Check if slot overlaps with busy period
            if slot_start < busy_end and slot_end > busy_start:
                return (period_status, subject)
        
        return ("available", "")
    
    def _ensure_naive_utc(self, dt: datetime) -> datetime:
        """
        Ensure datetime is naive UTC (no timezone info).
        
        Args:
            dt: Datetime (may be naive or timezone-aware)
            
        Returns:
            Naive UTC datetime
        """
        if dt is None:
            return None
        
        # If timezone-aware, convert to UTC and remove timezone
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc)
            dt = dt.replace(tzinfo=None)
        
        return dt
    
    def _format_subject(self, status: str, subject: str) -> str:
        """
        Format subject with emoji and default text for visual appeal.
        
        Args:
            status: Slot status ("available", "busy", "ooo")
            subject: Original subject text (may be empty)
            
        Returns:
            Formatted subject with emoji and appropriate text
        """
        if status == "available":
            return "✅ Вільний"
        elif status == "ooo":
            # If subject is already "Out of Office" or empty, use default
            if not subject or subject in ["Out of Office", "Busy"]:
                return "🏖️ Відпустка"
            return f"🏖️ {subject}"
        else:  # busy
            # If subject is empty or just "Busy", use default
            if not subject or subject == "Busy":
                return "📅 Зустріч"
            return f"📅 {subject}"
    
    def _group_slots(self, slots: List[TimelineSlot]) -> List[TimelineSlot]:
        """
        Group consecutive slots with same status and subject.
        
        Since subjects are already formatted with emoji, we can compare them directly.
        Same original subject will produce same formatted subject.
        
        Args:
            slots: List of timeline slots (already formatted with emoji)
            
        Returns:
            List of grouped timeline slots
        """
        if not slots:
            return []
        
        grouped_slots = []
        current_group = slots[0]
        
        for slot in slots[1:]:
            # Compare formatted subjects directly - same original subject = same formatted subject
            if (slot.status == current_group.status and 
                slot.subject == current_group.subject and
                current_group.end == slot.start):
                # Extend current group
                current_group = TimelineSlot(
                    time_range=(
                        f"{current_group.start.strftime('%H:%M')} - "
                        f"{slot.end.strftime('%H:%M')}"
                    ),
                    status=current_group.status,
                    subject=current_group.subject,  # Keep formatted subject
                    start=current_group.start,
                    end=slot.end
                )
            else:
                # Save current group and start new one
                grouped_slots.append(current_group)
                current_group = slot
        
        grouped_slots.append(current_group)
        return grouped_slots


__all__ = ["TimelineBuilder"]

