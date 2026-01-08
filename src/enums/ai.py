from enum import StrEnum


class AIProvider(StrEnum):
    OPENAI = "openai"
    

    @classmethod
    def cloud_providers(cls) -> list["AIProvider"]:
        """Returns a list of cloud-based AI providers"""
        return [
            cls.OPENAI,
            ]

