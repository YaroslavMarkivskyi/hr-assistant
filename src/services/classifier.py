

from interfaces import ai_service


class RequestClassifier:
    def __init__(self, ai_service: ai_service.AIService):
        self.ai_service = ai_service

