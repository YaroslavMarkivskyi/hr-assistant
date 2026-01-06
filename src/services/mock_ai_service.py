"""
Mock AI Service for Testing

A simple implementation of AIService protocol that returns predefined responses
without making actual API calls. Perfect for unit tests and offline development.

Usage in tests:
    from services.mock_ai_service import MockAIService
    mock_ai = MockAIService()
    container = ServiceContainer(..., ai_service=mock_ai, ...)
"""
from typing import Dict, Any, List
from interfaces.ai_service import AIService


class MockAIService:
    """
    Mock implementation of AIService for testing.
    
    Returns predefined responses without making API calls.
    Useful for:
    - Unit tests (no API costs, fast execution)
    - Offline development
    - CI/CD pipelines
    """
    
    def __init__(self, responses: Dict[str, Any] = None):
        """
        Initialize mock AI service with optional predefined responses.
        
        Args:
            responses: Dictionary mapping method names to return values
        """
        self.responses = responses or {}
    
    async def detect_intent(self, user_message: str) -> Dict[str, Any]:
        """Mock intent detection"""
        if "detect_intent" in self.responses:
            return self.responses["detect_intent"]
        
        # Default: detect onboarding if message contains keywords
        message_lower = user_message.lower()
        if any(keyword in message_lower for keyword in ["create", "onboard", "new user", "candidate"]):
            return {"intent": "onboarding", "entities": {}}
        elif any(keyword in message_lower for keyword in ["meeting", "schedule", "calendar"]):
            return {"intent": "schedule_meeting", "entities": {}}
        else:
            return {"intent": "chat", "entities": {}}
    
    async def parse_candidate_data(self, user_message: str) -> Dict[str, Any]:
        """Mock candidate data parsing"""
        if "parse_candidate_data" in self.responses:
            return self.responses["parse_candidate_data"]
        
        # Default: return mock candidate data
        return {
            "firstName": "John",
            "lastName": "Doe",
            "jobTitle": "Software Engineer",
            "department": "Engineering",
            "emailNickname": "johndoe",
            "personalEmail": "john.doe@example.com",
            "phoneNumber": "+1234567890"
        }
    
    async def parse_meeting_request(
        self, 
        user_message: str, 
        current_date: str | None = None
    ) -> Dict[str, Any]:
        """Mock meeting request parsing"""
        if "parse_meeting_request" in self.responses:
            response = self.responses["parse_meeting_request"]
            # Support both dict and callable responses
            if callable(response):
                return response(user_message, current_date)
            return response
        
        # Default: return mock meeting data
        # Use provided current_date or default mock date
        preferred_date = current_date or "2025-01-15"
        return {
            "participants": ["user@example.com"],
            "preferredDate": preferred_date,
            "preferredTime": "14:00",
            "duration": 60,
            "subject": "Team Meeting",
            "includeRequester": True
        }
    
    async def select_best_user_match(
        self, 
        user_query: str, 
        users: List[Dict]
    ) -> Dict[str, Any]:
        """Mock user matching"""
        if "select_best_user_match" in self.responses:
            return self.responses["select_best_user_match"]
        
        # Default: return first user
        if users:
            return {
                "success": True,
                "user": users[0],
                "confidence": "high",
                "reason": "Mock match"
            }
        return {"error": "No users provided"}
    
    async def generate_text(
        self,
        user_message: str,
        system_prompt: str | None = None,
        context: str | None = None
    ) -> str:
        """Mock text generation"""
        if "generate_text" in self.responses:
            response = self.responses["generate_text"]
            # Support both string and callable responses
            if callable(response):
                return response(user_message, system_prompt, context)
            return str(response)
        
        # Default: return a friendly mock response
        message_lower = user_message.lower()
        if any(word in message_lower for word in ["hello", "hi", "привіт", "вітаю"]):
            return "Hello! How can I help you today?"
        elif any(word in message_lower for word in ["how are you", "як справи", "як ти"]):
            return "I'm doing great! Ready to help with HR tasks. What do you need?"
        elif any(word in message_lower for word in ["joke", "жарт", "анекдот"]):
            return "Why did the HR bot go to therapy? Because it had too many unresolved intents! 😄"
        else:
            return f"Mock response to: {user_message[:50]}..."


