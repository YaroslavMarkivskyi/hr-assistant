

from interfaces import ai_service
from botframework.core import TurnContext


class RequestClassifier:
    def __init__(self, ai_service: ai_service.AIService):
        self.ai_service = ai_service

    async def classify(self, turn_context: "TurnContext") -> "ClassificationResult":
        pass