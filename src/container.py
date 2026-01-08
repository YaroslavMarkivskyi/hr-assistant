"""
Service container for dependency injection.
Fixes ImportError by using the new registry initialization logic.
"""
from dataclasses import dataclass
from typing import TYPE_CHECKING
import logging

from services.graph_service import GraphService
from services.email_service import EmailService
# from services.openai_service import OpenAIService
from services.ai import AIService
from services.user_search import UserSearchService
from services.time import TimeService
from db.database import DatabaseService
from handlers.dispatcher import BotDispatcher
# 1. FIX: Removed register_module, Added initialize_controllers
from handlers.registry import initialize_controllers, GENERAL_MODULE
from config import Config

if TYPE_CHECKING:
    from interfaces.ai_service import AIService
    from features.scheduling.service import SchedulingService

logger = logging.getLogger("HRBot")

@dataclass
class ServiceContainer:
    """
    Container for all bot services.
    Provides dependency injection pattern for handlers.
    """
    graph_service: GraphService
    email_service: EmailService
    ai_service: AIService
    user_search_service: UserSearchService
    scheduling_service: "SchedulingService"
    db_service: DatabaseService
    dispatcher: BotDispatcher
    config: Config
    time_service: TimeService
      
    @classmethod
    def create(cls, config: Config) -> 'ServiceContainer':
        """
        Factory method to create a service container with initialized services.
        Now also handles Controller Initialization via Dependency Injection.
        """
        # 1. Create Base Services
        ai_service = AIService(config)
        graph_service = GraphService(config)
        email_service = EmailService(config)
        db_service = DatabaseService(db_path=config.DB_PATH)
        time_service = TimeService()
        # 2. Create Composite Services
        user_search_service = UserSearchService(
            graph_service=graph_service,
            ai_service=ai_service
        )
        
        # Lazy import to avoid circular dependency
        from features.scheduling.service import SchedulingService
        scheduling_service = SchedulingService(
            graph_service=graph_service,
            user_search_service=user_search_service
        )
        
        # 3. Create Dispatcher
        dispatcher = BotDispatcher()
        
        # 4. Create Container Instance
        # Ми створюємо об'єкт контейнера ТУТ, щоб мати змогу передати його в initialize_controllers
        container = cls(
            graph_service=graph_service,
            email_service=email_service,
            time_service=time_service,
            ai_service=ai_service,
            user_search_service=user_search_service,
            scheduling_service=scheduling_service,
            db_service=db_service,
            dispatcher=dispatcher,
            config=config
        )

        # 5. Register Controllers (Import Trigger)
        # Імпортуємо модулі, щоб спрацювали декоратори @register_controller
        # Вони наповнять словник _REGISTERED_CLASSES в registry.py
        try:
            from features.scheduling.controller import SchedulingController  # noqa: F401
            from handlers.general import GeneralController  # noqa: F401
            logger.info("Controllers modules imported successfully.")
        except ImportError as e:
            logger.error(f"Failed to import controllers: {e}")
            raise

        # 6. Initialize Controllers (Dependency Injection)
        # Тепер, коли у нас є і класи контролерів, і готовий контейнер з сервісами,
        # ми пов'язуємо їх разом.
        initialize_controllers(container)
        
        return container