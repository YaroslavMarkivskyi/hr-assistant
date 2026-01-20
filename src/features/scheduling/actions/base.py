from __future__ import annotations
import logging

from abc import ABC, abstractmethod

from typing import Generic, TypeVar, TYPE_CHECKING

from ..schemas import requests as request_schemas
from ..schemas import responses as response_schemas


if TYPE_CHECKING:
    from services.graph_service import GraphService
    

logger = logging.getLogger(__name__)


TRequest = TypeVar("TRequest", bound=request_schemas.BaseSchedulingRequest)
TResponse = TypeVar("TResponse", bound=response_schemas.BaseSchedulingResponse)


class BaseSchedulingAction(ABC, Generic[TRequest, TResponse]):
    """
    Abstract base class for scheduling actions.
    """

    def __init__(self, graph_service: GraphService):
        self._graph_service = graph_service

    @abstractmethod
    async def execute(
        self, 
        request: TRequest
        ) -> response_schemas.SchedulingResult[TResponse]:
        """
        Executes the action with the given request.
        
        Args:
            request: The request data for the action.
            
        Returns:
            The response data from the action.
        """
        action_name = self.__class__.__name__
        logger.info(f"Executing action: {action_name} with request: {request}")
        
        try:
            result = await self._run(request)
            
            if result.success:
                logger.info(f"Action {action_name} completed successfully.")
            else:
                logger.warning(f"Action {action_name} failed with error: {result.error_message}")
            
            return result
        except Exception as e:
            logger.error(f"Exception during action {action_name}: {e}", exc_info=True)
            return response_schemas.SchedulingResult(
                success=False,
                error_message=str(e),
            )
    
    @abstractmethod
    async def _run(
        self,
        request: TRequest
        ) -> response_schemas.SchedulingResult[TResponse]:
        pass
            

__all__ = (
    "BaseSchedulingAction",
)

