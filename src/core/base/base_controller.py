import logging

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from core.containers.service_container import ServiceContainer
    from bot.activity_context_wrapper import ActivityContextWrapper
    from schemas.bot import ActionPayload, IntentPayload
    

logger = logging.getLogger(__name__)


class BaseController(ABC):
    """
    Abstract base class for all module controllers.
    Defines the interface for handling actions and intents.
    """
    def __init__(self, container: "ServiceContainer") -> None:
        self._container = container

    @abstractmethod
    async def handle_action(
        self,
        ctx: "ActivityContextWrapper",
        payload: ActionPayload,
        container: "ServiceContainer"
    ) -> None:
        """
        Handle an action (button click) from the user.
        """
        pass

    @abstractmethod
    async def handle_intent(
        self,
        ctx: "ActivityContextWrapper",
        intent: str,
        ai_response: Any,
        container: "ServiceContainer"
    ) -> None:
        """
        Handle an intent recognized from user input.
        """
        pass