from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from .base import BaseSchedulingAction

from ..schemas import requests as request_schemas
from ..schemas import responses as response_schemas

if TYPE_CHECKING:
    # from services.graph_service import GraphService
    pass


logger = logging.getLogger(__name__)


class CancelMeetingAction(
    BaseSchedulingAction[
        request_schemas.CancelMeetingRequest,
        response_schemas.CancelMeetingResponse
    ]
):
    async def _run(
        self,
        request: request_schemas.CancelMeetingRequest
    ) -> response_schemas.SchedulingResult[response_schemas.CancelMeetingResponse]:
        logger.info(f"MOCK: Cancelling meeting with ID: {request.meeting_id}")
        cancelled_meeting = response_schemas.CancelMeetingResponse(
            meeting_id=request.meeting_id,
            status="Cancelled"
        )
        return response_schemas.SchedulingResult(
            success=True,
            data=cancelled_meeting
        )
__all__ = (
    "CancelMeetingAction",
)

