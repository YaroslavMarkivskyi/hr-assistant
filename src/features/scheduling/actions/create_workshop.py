import logging
from services.graph_service import GraphService
from ..models import SchedulingResult, CreateWorkshopRequest, CreateWorkshopData

logger = logging.getLogger("HRBot")

class CreateWorkshopAction:
    def __init__(self, graph_service: GraphService):
        self.graph_service = graph_service

    async def execute(self, request: CreateWorkshopRequest) -> SchedulingResult[CreateWorkshopData]:
        # STUB: To be implemented
        logger.info(f"STUB: Creating workshop '{request.subject}'")
        
        return SchedulingResult(
            success=False,
            error="CreateWorkshopAction is not yet implemented."
        )
        
__all__ = ["CreateWorkshopAction"]

