"""
Module Registry - maps modules to their controllers.

Supports Dependency Injection by separating class registration from instantiation.
"""
from typing import Dict, Protocol, Type, Optional, TYPE_CHECKING
import logging
from enums.bot import BotModule
from models.action import ActionPayload
from models.ai import AIResponse

if TYPE_CHECKING:
    from bot.activity_context_wrapper import ActivityContextWrapper
    from core.containers.service_container import ServiceContainer

# Constant for General module
GENERAL_MODULE = None


class ModuleController(Protocol):
    """Protocol for module controllers."""
    async def handle_action(self, ctx: "ActivityContextWrapper", payload: ActionPayload, container: "ServiceContainer") -> None: ...
    async def handle_intent(self, ctx: "ActivityContextWrapper", intent: str, ai_response: AIResponse, container: "ServiceContainer") -> None: ...


_REGISTERED_CLASSES: Dict[BotModule | None, Type[ModuleController]] = {}

_MODULE_CONTROLLERS: Dict[BotModule | None, ModuleController] = {}


def register_controller(module: BotModule | None):
    """
    Decorator to register a controller CLASS.
    Does NOT instantiate it immediately.
    """
    def decorator(controller_class: Type[ModuleController]) -> Type[ModuleController]:
        if module in _REGISTERED_CLASSES:
            raise ValueError(f"Module {module} is already registered")
        
        _REGISTERED_CLASSES[module] = controller_class
        return controller_class
    return decorator


def initialize_controllers(container: "ServiceContainer") -> None:
    """
    Factory function to instantiate all registered controllers with their dependencies.
    Must be called at application startup after Container is ready.
    """
    logger = logging.getLogger("HRBot")
    
    for module, cls in _REGISTERED_CLASSES.items():
        try:
            # --- DEPENDENCY INJECTION LOGIC ---
            if module == BotModule.SCHEDULING:
                # SchedulingController вимагає SchedulingService
                instance = cls(service=container.scheduling_service)    
            else:
                logger.warning(f"Initializing {cls.__name__} without service dependency.")
                instance = cls(service=None)

            _MODULE_CONTROLLERS[module] = instance
            logger.info(f"✅ Controller initialized: {cls.__name__} for module {module}")
            
        except TypeError as e:
            logger.error(f"❌ Failed to initialize {cls.__name__}. Check __init__ arguments! Error: {e}")
            raise

def get_controller(module: BotModule | None) -> Optional[ModuleController]:
    """Get the initialized controller instance."""
    return _MODULE_CONTROLLERS.get(module)