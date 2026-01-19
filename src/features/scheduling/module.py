from __future__ import annotations
from typing import TYPE_CHECKING

from core.base import BaseModule

from .controller import SchedulingController
from .service import SchedulingService


if TYPE_CHECKING:
    from core.containers.service_container import ServiceContainer

class SchedulingModule(BaseModule):
    def __init__(self, container: ServiceContainer):
        
        self._service = SchedulingService(
            graph_service=container.graph,
            user_search_service=container.user_search
        )
        
        controller = SchedulingController(
            container=container,
            service=self._service
        )
        
        super().__init__(controller=controller)
    

__all__ = ("SchedulingModule",)

