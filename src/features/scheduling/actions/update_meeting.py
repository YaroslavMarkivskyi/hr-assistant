from __future__ import annotations
import logging

from typing import TYPE_CHECKING, List

from .base import BaseSchedulingAction

from ..schemas import requests as request_schemas
from ..schemas import responses as response_schemas

if TYPE_CHECKING:
    # from services.graph_service import GraphService
    pass
    
    
logger = logging.getLogger(__name__)


class UpdateMeetingAction(
    BaseSchedulingAction[
        request_schemas.UpdateMeetingRequest,
        response_schemas.UpdateMeetingResponse
    ]
):
    async def _run(
        self,
        request: request_schemas.UpdateMeetingRequest
    ) -> response_schemas.SchedulingResult[response_schemas.UpdateMeetingResponse]:
        # TODO: Implement the logic to update a meeting using the GraphService
        logger.info(f"MOCK Updating meeting with ID: {request.meeting_id}")
        updated_meeting = response_schemas.UpdateMeetingResponse(
            meeting_id=request.meeting_id,
            status="Updated"
        )
        
        return response_schemas.SchedulingResult(
            success=True,
            data=updated_meeting
        )
        
__all__ = (
    "UpdateMeetingAction",
)

