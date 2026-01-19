import logging
from dataclasses import dataclass, field
from typing import Dict, TYPE_CHECKING

from core.config import Config
from core.enums.bot import BotModule
from core.base import BaseModule

from services.ai import AIService
from services.email_service import EmailService
from services.graph_service import GraphService
from services.time import TimeService
from services.user_search import UserSearchService
from services.classifier import RequestClassifier
from db.database import DatabaseService
from handlers.dispatcher import BotDispatcher


if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)


@dataclass
class ServiceContainer:
    """
    Container for all bot services.
    Provides dependency injection pattern for handlers.
    """
    config: Config
    db: DatabaseService
    ai: AIService
    graph: GraphService
    email: EmailService
    time: TimeService
    
    user_search: UserSearchService
    classifier: RequestClassifier
    dispatcher: BotDispatcher
    
    features: Dict[BotModule, BaseModule] = field(default_factory=dict)

    @classmethod
    def create(cls, config: Config) -> 'ServiceContainer':
        """
        Factory method to create a service container with initialized services.
        """
        # Initialize core services
        from .feature_registry import initialize_features
        logger.info("Initializing core services...")
        
        # Base services
        db = DatabaseService(db_path=config.DB_PATH)
        ai = AIService(config)
        graph = GraphService(config)
        email = EmailService(config)
        time = TimeService()
        
        # System services
        classifier = RequestClassifier(ai_service=ai)
        dispatcher = BotDispatcher()
        
        # Composite services
        user_search = UserSearchService(
            graph_service=graph,
            ai_service=ai
        )
        features = initialize_features(config)
        container = cls(
            config=config,
            db=db,
            ai=ai,
            graph=graph,
            email=email,
            time=time,
            user_search=user_search,
            classifier=classifier,
            dispatcher=dispatcher,
            features=features,
        )
        
        return container
        

__all__ = (
    "ServiceContainer",
)

