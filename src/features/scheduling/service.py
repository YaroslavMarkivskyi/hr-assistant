from __future__ import annotations
import logging

from typing import Dict, Type, TYPE_CHECKING

from .schemas import requests as request_schemas
from .schemas import responses as response_schemas

from . import actions as scheduling_actions

from .services import TimelineBuilder


if TYPE_CHECKING:
    from services.graph_service import GraphService
    from services.user_search import UserSearchService
    from .actions import BaseSchedulingAction
    

logger = logging.getLogger(__name__)


class SchedulingService:
    def __init__(
        self,
        graph_service: GraphService,
        user_search_service: UserSearchService
    ):
        self._graph_service = graph_service
        self._user_search_service = user_search_service
        self._timeline_builder = TimelineBuilder()
        
        # TODO: Change in the future to new registration system
        self._action_classes: Dict[
            str, 
            Type[BaseSchedulingAction[
                request_schemas.BaseSchedulingRequest,
                response_schemas.BaseSchedulingResponse
            ]]
            ] = {
            "find_time": scheduling_actions.FindTimeAction,
            "book": scheduling_actions.BookMeetingAction,
            "briefing": scheduling_actions.DailyBriefingAction,
            "update": scheduling_actions.UpdateMeetingAction,
            "cancel": scheduling_actions.CancelMeetingAction,
            "workshop": scheduling_actions.CreateWorkshopAction,
            "view": scheduling_actions.ViewScheduleAction,
        }

        self._action_instances: Dict[
            str, BaseSchedulingAction[
                request_schemas.BaseSchedulingRequest,
                response_schemas.BaseSchedulingResponse
                ]
            ] = {}

    def _get_action_instance(
        self, 
        action_name: str
        ) -> BaseSchedulingAction[
            request_schemas.BaseSchedulingRequest,
            response_schemas.BaseSchedulingResponse
            ]:
        if action_name not in self._action_instances:
            action_class = self._action_classes[action_name]
            if action_name == "view":
                instance = action_class(
                    self._graph_service,
                    self._user_search_service,
                    self._timeline_builder
                )
            elif action_name == "find_time":
                instance = action_class(
                    self._graph_service,
                    self._user_search_service
                )
            else:
                instance = action_class(self._graph_service)
            
            self._action_instances[action_name] = instance
        return self._action_instances[action_name]
    
    async def find_time(
        self,
        request: request_schemas.FindTimeRequest
    ) -> response_schemas.SchedulingResult[response_schemas.FindTimeResponse]:
        action = self._get_action_instance("find_time")
        return await action.execute(request)
    
    async def book_meeting(
        self,
        request: request_schemas.BookMeetingRequest,
    ) -> response_schemas.SchedulingResult[response_schemas.BookMeetingResponse]:
        action = self._get_action_instance("book")
        return await action.execute(request)
    
    async def view_schedule(
        self,
        request: request_schemas.ViewScheduleRequest
    ) -> response_schemas.SchedulingResult[response_schemas.ViewScheduleResponse]:
        action = self._get_action_instance("view")
        return await action.execute(request)
    
    async def daily_briefing(
        self,
        request: request_schemas.DailyBriefingRequest
    ) -> response_schemas.SchedulingResult[response_schemas.DailyBriefingResponse]:
        action = self._get_action_instance("briefing")
        return await action.execute(request)
    
    async def update_meeting(
        self,
        request: request_schemas.UpdateMeetingRequest
    ) -> response_schemas.SchedulingResult[response_schemas.UpdateMeetingResponse]:
        action = self._get_action_instance("update")
        return await action.execute(request)
    
    async def cancel_meeting(
        self,
        request: request_schemas.CancelMeetingRequest
    ) -> response_schemas.SchedulingResult[response_schemas.CancelMeetingResponse]:
        action = self._get_action_instance("cancel")
        return await action.execute(request)


__all__ = (
    "SchedulingService",
)

