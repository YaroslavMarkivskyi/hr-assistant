"""
AI Service Protocol (Interface)

Defines the contract for the Generic AI Service.
This allows strictly typed dependency injection and easy mocking for tests.
"""
from typing import Protocol, Type, TypeVar, Optional, Any
from pydantic import BaseModel

from schemas.ai import UserIntent


# Generic type for Pydantic models
T = TypeVar("T", bound=BaseModel)

class AIService(Protocol):
    """
    Protocol defining the interface for the Universal AI Service.
    """

    async def extract_data(
        self,
        user_text: str,
        result_type: Type[T],
        prompt_key: str | Any, # Any, бо PromptKey - це Enum, який може не бути тут імпортований
        context: Optional[str] = None
    ) -> T:
        """
        Extract structured data from user text using a specific Pydantic model.
        """
        ...

    async def chat(
        self,
        user_text: str,
        prompt_key: str | Any = "chat",
        context: Optional[str] = None
    ) -> str:
        """
        Generate conversational chat response (unstructured text).
        """
        ...
        
    async def detect_intent(
        self, 
        user_text: str, 
        context: Optional[str] = None
    ) -> UserIntent:
        """
        Detect user intent (specialized wrapper around extract_data).
        """
        ...