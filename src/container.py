"""
Service container for dependency injection
"""
from dataclasses import dataclass
from services.graph_service import GraphService
from services.email_service import EmailService
from services.openai_service import OpenAIService
from config import Config


@dataclass
class ServiceContainer:
    """
    Container for all bot services.
    Provides dependency injection pattern for handlers.
    """
    graph_service: GraphService
    email_service: EmailService
    openai_service: OpenAIService
    config: Config
    
    @classmethod
    def create(cls, config: Config) -> 'ServiceContainer':
        """
        Factory method to create a service container with initialized services
        
        Args:
            config: Application configuration
            
        Returns:
            ServiceContainer with all services initialized
        """
        return cls(
            graph_service=GraphService(config),
            email_service=EmailService(config),
            openai_service=OpenAIService(config),
            config=config
        )

