from dataclasses import dataclass

from .base_controller import BaseController


@dataclass
class BaseModule:
    """
    Base class for all modules in the service container.
    """
    controller: BaseController


__all__ = (
    "BaseModule",
)

