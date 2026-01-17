from services.graph_service import GraphService
from services.user_search import UserSearchService
from .repository import TimeOffRepository


class TimeOffService:
    def __init__(
        self,
        graph_service: GraphService,
        time_off_repository: TimeOffRepository,
        user_search_service: UserSearchService
    ):
        self._graph_service = graph_service
        self._time_off_repository = time_off_repository
        self._user_search_service = user_search_service


__all__ = ["TimeOffService"]

