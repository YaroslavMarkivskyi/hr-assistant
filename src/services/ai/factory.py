import logging
from typing import Dict, Callable

from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel

from config import Config
from enums.ai import AIProvider


logger = logging.getLogger(__name__)


class AIModelFactory:
    """
    Factory class to create AI model instances.
    Encapsulates specific client initialization logic (OpenAI vs Azure vs others).
    """
    
    @classmethod
    def create_model(cls, config: Config) -> Model:        
        logger.info(f"🏭 AI Factory: Initializing {config.AI_PROVIDER} with model '{config.AI_MODEL_NAME}'")
        
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

    # =========================================================================
    # REGISTRY
    # =========================================================================

    @classmethod
    def _get_builders(cls) -> Dict[AIProvider, Callable[[Config], Model]]:
        """Maps providers to their builder methods."""
        return {
            AIProvider.OPENAI: cls._build_openai_model,
            # AIProvider.AZURE: cls._build_azure_model,
            # AIProvider.ANTHROPIC: cls._build_anthropic_model,
        }
        
        
__all__ = ["AIModelFactory"]

