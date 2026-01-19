"""
Scheduling Service - Business logic layer for scheduling operations.

This service acts as a FACADE. It orchestrates scheduling operations by delegating 
complex logic to specific Action classes (Command Pattern) or utility builders.

It does NOT know about bot context or UI (Adaptive Cards).
It accepts pure data (strings, dates) and returns model objects.
"""
import logging
from typing import List, Optional, Union
from datetime import datetime

from services.graph_service import GraphService
from services.user_search import UserSearchService
from .schemas import (
    SchedulingResult, 
    Participant,
    FindTimeRequest,
    FindTimeData,
    BookMeetingRequest,
    BookMeetingData,
    DailyBriefingRequest,
    DailyBriefingData,
    ViewScheduleRequest,
    ViewScheduleData,
    UpdateMeetingRequest,
    UpdateMeetingData,
    CancelMeetingRequest,
    CancelMeetingData,
    CreateWorkshopRequest,
    CreateWorkshopData
)
from .services import TimelineBuilder
from .actions import (
    FindTimeAction,
    BookMeetingAction,
    DailyBriefingAction,
    ViewScheduleAction,
    UpdateMeetingAction,
    CancelMeetingAction,
    CreateWorkshopAction
)

logger = logging.getLogger("HRBot")


class SchedulingService:
    """
    Service for scheduling operations.
    Acts as a central entry point (Facade) for the controller.
    """
    
    def __init__(
        self,
        graph_service: GraphService,
        user_search_service: UserSearchService
    ):
        """
        Initialize scheduling service and its actions.
        """
        self.graph_service = graph_service
        self.user_search_service = user_search_service
        
        # Helpers & Builders
        self.timeline_builder = TimelineBuilder()
        
        # Actions (Command Pattern)
        self._find_time_action = FindTimeAction(graph_service, user_search_service)
        self._book_meeting_action = BookMeetingAction(graph_service)
        self._daily_briefing_action = DailyBriefingAction(graph_service)
        self._update_meeting_action = UpdateMeetingAction(graph_service)
        self._cancel_meeting_action = CancelMeetingAction(graph_service)
        self._create_workshop_action = CreateWorkshopAction(graph_service)
        self._view_schedule_action = ViewScheduleAction(
            graph_service, 
            user_search_service,
            self.timeline_builder
        )
    
    async def find_time(self, request: FindTimeRequest) -> SchedulingResult[FindTimeData]:
        """
        Find available time slots for a meeting.
        Delegates logic to FindTimeAction.
        """
        return await self._find_time_action.execute(request)
    
    async def book_meeting(
        self,
        requester_id: str,
        subject: str,
        participants: List[Participant],
        start_time: datetime,
        end_time: datetime,
        agenda: Optional[str] = None
    ) -> SchedulingResult[BookMeetingData]:
        """
        Book/create a meeting with Teams link.
        Delegates logic to BookMeetingAction.
        """
        request = BookMeetingRequest(
            requester_id=requester_id,
            subject=subject,
            participants=participants,
            start_time=start_time,
            end_time=end_time,
            agenda=agenda
        )
        
        return await self._book_meeting_action.execute(request)
    
    async def update_meeting(
        self,
        requester_id: str,
        meeting_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        subject: Optional[str] = None,
        participants: Optional[List[Participant]] = None
    ) -> SchedulingResult[UpdateMeetingData]:
        """
        Update/reschedule an existing meeting.
        """
        request = UpdateMeetingRequest(
            requester_id=requester_id,
            meeting_id=meeting_id,
            start_time=start_time,
            end_time=end_time,
            subject=subject,
            participants=participants
        )
        
        return await self._update_meeting_action.execute(request)
    
    async def cancel_meeting(
        self,
        requester_id: str,
        meeting_id: str
    ) -> SchedulingResult[CancelMeetingData]:
        """
        Cancel an existing meeting.
        """
        request = CancelMeetingRequest(
            requester_id=requester_id,
            meeting_id=meeting_id
        )
        
        return await self._cancel_meeting_action.execute(request)
    
    async def create_workshop(
        self,
        requester_id: str,
        subject: str,
        participants: List[Participant],
        start_time: datetime,
        end_time: datetime,
        ignore_availability: bool = False
    ) -> SchedulingResult[CreateWorkshopData]:
        """
        Create a workshop/lecture (broadcast mode).
        """
        request = CreateWorkshopRequest(
            requester_id=requester_id,
            subject=subject,
            participants=participants,
            start_time=start_time,
            end_time=end_time,
            ignore_availability=ignore_availability
        )
        
        return await self._create_workshop_action.execute(request)
    
    async def daily_briefing(
        self,
        requester_id: str,
        date: Optional[Union[str, datetime]] = None
    ) -> SchedulingResult[DailyBriefingData]:
        """
        Get daily calendar briefing for a user.
        """
        request = DailyBriefingRequest(
            requester_id=requester_id,
            date=date
        )
        
        return await self._daily_briefing_action.execute(request)
    
    async def view_schedule(
        self,
        requester_id: str,
        employee_id: Optional[str] = None,
        employee_name: Optional[str] = None,
        date: Optional[Union[str, datetime]] = None,
        detailed: bool = False
    ) -> SchedulingResult[ViewScheduleData]:
        """
        View employee schedule (Free/Busy or detailed).
        Uses TimelineBuilder for visualization logic.
        """
        request = ViewScheduleRequest(
            requester_id=requester_id,
            employee_id=employee_id,
            employee_name=employee_name,
            date=date,
            detailed=detailed
        )
        
        return await self._view_schedule_action.execute(request)
    

__all__ = ["SchedulingService"]