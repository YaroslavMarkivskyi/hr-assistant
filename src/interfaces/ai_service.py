"""
AI Service Protocol (Interface)

Defines the contract that any AI service implementation must follow.
This allows the bot to work with any LLM provider (OpenAI, Azure OpenAI, 
Anthropic, Google Gemini, local models, etc.) without code changes.

Usage:
    - OpenAIService implements this protocol
    - MockAIService (for tests) implements this protocol
    - Future: AzureOpenAIService, AnthropicService, etc.
"""
from typing import Protocol, Dict, Any, List


class AIService(Protocol):
    """
    Protocol defining the interface for AI services.
    
    Any class implementing these methods can be used as an AI service,
    making the bot vendor-agnostic and easily testable.
    """
    
    async def detect_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Detect user intent from a message.
        
        Args:
            user_message: User's message text
            
        Returns:
            Dictionary with "intent" and "entities" keys.
            Example: {"intent": "onboarding", "entities": {}}
        """
        ...
    
    async def parse_candidate_data(self, user_message: str) -> Dict[str, Any]:
        """
        Parse candidate/employee data from a message.
        
        Args:
            user_message: Message containing candidate information
            
        Returns:
            Dictionary with candidate fields (firstName, lastName, jobTitle, etc.)
            or {"error": "..."} if parsing fails
        """
        ...
    
    async def parse_meeting_request(
        self, 
        user_message: str, 
        current_date: str | None = None
    ) -> Dict[str, Any]:
        """
        Parse meeting scheduling request from a message.
        
        Args:
            user_message: Message containing meeting details
            current_date: Optional current date in ISO format (YYYY-MM-DD).
                        If None, uses current system date.
                        Useful for testing or when you need a specific reference date.
            
        Returns:
            Dictionary with meeting fields (participants, preferredDate, etc.)
            or {"error": "..."} if parsing fails
        """
        ...
    
    async def select_best_user_match(
        self, 
        user_query: str, 
        users: List[Dict]
    ) -> Dict[str, Any]:
        """
        Select the best matching user from a list using AI.
        
        Args:
            user_query: Search query from user
            users: List of user dictionaries to match against
            
        Returns:
            Dictionary with "success", "user", "confidence", "reason" keys
            or {"error": "..."} if matching fails
        """
        ...
    
    async def generate_text(
        self,
        user_message: str,
        system_prompt: str | None = None,
        context: str | None = None
    ) -> str:
        """
        Generate unstructured text response for conversational chat.
        
        This method is used for:
        - General conversation ("How are you?", "Tell me a joke")
        - Fallback responses when structured parsing fails
        - Knowledge base queries that need natural language answers
        - Friendly, human-like interactions
        
        Args:
            user_message: User's message or question
            system_prompt: Optional system prompt to set AI behavior/personality
            context: Optional context information (e.g., user's previous messages, 
                    knowledge base content) to help generate better responses
            
        Returns:
            Generated text response (plain string, not JSON)
            
        Example:
            >>> response = await ai_service.generate_text(
            ...     "How are you?",
            ...     system_prompt="You are a friendly HR assistant."
            ... )
            >>> print(response)
            "I'm doing great! How can I help you today?"
        """
        ...


