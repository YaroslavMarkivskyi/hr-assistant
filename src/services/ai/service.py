import logging
from pathlib import Path
from typing import Optional, TypeVar, Type, Any, Dict

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models import Model

from config import Config
from .factory import AIModelFactory
from schemas.ai import UserIntent
from enums.prompts import PromptKeys

logger = logging.getLogger(__name__)


# Generic type for AIService
T = TypeVar("T", bound=BaseModel)


class AIService:
    """
    Vendor-agnostic AI Service.
    Uses 'pydantic-ai' to manage Agents and structured data extraction.
    """
    def __init__(self, config: Config):
        self._config = config
        self._model: Model = AIModelFactory.create_model(config)
        self._prompts_dir = Path(__file__).resolve().parent.parent.parent / "prompts"
        self._prompts_cache: Dict[str, str] = {}
        
    async def extract_data(
        self,
        user_text: str,
        result_type: Type[T],
        prompt_key: str,
        context: Optional[str] = None
    ) -> T:
        """
        Extract structured data from user text using an Agent.
        """
        try:
            system_prompt = self._build_system_prompt(prompt_key, context)
            
            agent = Agent(
                self._model,
                output_type=result_type,
                system_prompt=system_prompt,
                retries=self._config.AI_MAX_RETRIES
            )
            logger.info(f"🤖 AI Service: Extracting data with prompt '{prompt_key}'")
            
            result = await agent.run(user_text)
            logger.info(f"🧠 AI Service: Extraction result - {result.output}")
            return result.output
        except Exception as e:
            logger.error(f"❌ AI Service: Data extraction failed - {e}", exc_info=True)
            return result_type.model_construct()
        
    async def chat(
        self,
        user_text: str,
        prompt_key: str = "chat",
        context: Optional[str] = None
    ) -> str:
        """
        Generate conversational chat response.
        """
        try:
            system_prompt = self._build_system_prompt(prompt_key, context)
                        
            agent = Agent(
                self._model,
                system_prompt=system_prompt,
                retries=self._config.AI_MAX_RETRIES
            )
            logger.info(f"🤖 AI Service: Generating chat response with prompt '{prompt_key}'")
            
            result = await agent.run(user_text)
            return result.data
        except Exception as e:
            logger.error(f"❌ AI Service: Chat generation failed - {e}", exc_info=True)
            return "I'm sorry, I couldn't process your request at the moment."

    async def detect_intent(
        self,
        user_text: str,
        context: Optional[str] = None
    ) -> UserIntent:
        """
        Step 1: Classification using Router prompt.
        """
        return await self.extract_data(
            user_text,
            result_type=UserIntent,
            prompt_key=PromptKeys.ROUTER,
            context=context
        )

    def _build_system_prompt(self, prompt_key: str, context: Optional[str]) -> str:
        """
        Build system prompt with optional context.
        """
        system_prompt = self._get_prompt_text(prompt_key)
        if context:
            system_prompt = f"{system_prompt}\n\nCONTEXT:\n{context}"
        return system_prompt
        
    def _get_prompt_text(self, prompt_key: str) -> str:
        """
        Load prompt text from file or cache.
        """
        if prompt_key in self._prompts_cache:
            return self._prompts_cache[prompt_key]
        
        filename = prompt_key if prompt_key.endswith(".txt") else f"{prompt_key}.txt"
        file_path = self._prompts_dir / filename
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                prompt_text = f.read()
                self._prompts_cache[prompt_key] = prompt_text
                return prompt_text    
        except FileNotFoundError:
            logger.error(f"❌ AI Service: Prompt file '{filename}' not found.")
            return "You are a helpful AI assistant."
        

__all__ = ["AIService"]

