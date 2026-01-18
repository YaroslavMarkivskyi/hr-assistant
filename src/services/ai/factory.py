import logging
from typing import Dict, Callable

from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel

from core.config import Config
from core.enums.ai import AIProvider


logger = logging.getLogger(__name__)


class AIModelFactory:
    """
    Factory class to create AI model instances.
    Encapsulates specific client initialization logic (OpenAI vs Azure vs others).
    """
    
    @classmethod
    def create_model(cls, config: Config) -> Model:        
        logger.info(f"AI Factory: Initializing {config.AI_PROVIDER} with model '{config.AI_MODEL_NAME}'")
        
        builder = cls._get_builders().get(config.AI_PROVIDER)
        
        if not builder:
            raise ValueError(f"Unsupported AI provider: {config.AI_PROVIDER}")
        
        return builder(config)
    
    # =========================================================================
    # BUILDERS (High-level Logic)
    # =========================================================================
    
    @classmethod
    def _build_openai_model(cls, config: Config) -> Model:
        """Builds OpenAI model with proper AsyncClient."""
        
        from openai import AsyncOpenAI
        if config.AI_API_KEY:
            AsyncOpenAI.api_key = config.AI_API_KEY
            
        if config.AI_API_BASE_URL:
            AsyncOpenAI.base_url = config.AI_API_BASE_URL
        
        return OpenAIChatModel(
            model_name=config.AI_MODEL_NAME
        )
        
    @classmethod
    def _build_azure_model(cls, config: Config) -> Model:
        """Builds Azure OpenAI model with proper AsyncClient."""
        
        from openai import AsyncAzureOpenAI
        
        if not config.AI_API_KEY:
            raise ValueError("AI_API_KEY is required for Azure provider")
        if not config.AI_BASE_URL:
            raise ValueError("AI_BASE_URL is required for Azure provider")
        if not config.AI_API_VERSION:
            raise ValueError("AI_API_VERSION is required for Azure provider")
        
        client = AsyncAzureOpenAI(
            api_key=config.AI_API_KEY,
            base_url=config.AI_BASE_URL,
            api_version=config.AI_API_VERSION
        )
        return OpenAIChatModel(
            model_name=config.AI_MODEL_NAME,
            client=client
        )
    

    # =========================================================================
    # REGISTRY
    # =========================================================================

    @classmethod
    def _get_builders(cls) -> Dict[AIProvider, Callable[[Config], Model]]:
        """Maps providers to their builder methods."""
        return {
            AIProvider.OPENAI: cls._build_openai_model,
            AIProvider.AZURE: cls._build_azure_model,
        }
        

__all__ = ["AIModelFactory"]

