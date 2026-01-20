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


class CreateWorkshopAction(
    BaseSchedulingAction[
        request_schemas.CreateWorkshopRequest,
        response_schemas.CreateWorkshopResponse
    ]
):
    async def _run(
        self,
        request: request_schemas.CreateWorkshopRequest
    ) -> response_schemas.SchedulingResult[response_schemas.CreateWorkshopResponse]:
        logger.info(f"MOCK: Creating workshop with ID: {request.workshop_id}")
        created_workshop = response_schemas.CreateWorkshopResponse(
            workshop_id=request.workshop_id,
            status="Created"
        )
        return response_schemas.SchedulingResult(
            success=True,
            data=created_workshop
        )
        
__all__ = (
    "CreateWorkshopAction",
)

