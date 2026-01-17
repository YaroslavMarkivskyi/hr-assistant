"""
Application Configuration Module

Organized into logical configuration classes for better maintainability.
Refactored for Vendor-Agnostic AI support (OpenAI, Gemini, Ollama, etc.)
and strict security practices (SecretStr).
"""
import logging
from typing import Optional
from pathlib import Path
from pydantic import Field, AliasChoices, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from core.enums.ai import AIProvider


logger = logging.getLogger(__name__)

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_DIR = BASE_DIR / "env"


# --- Configuration Classes ---

class AzureBotConfig(BaseSettings):
    """Azure Bot Framework configuration"""
    
    APP_ID: str = Field(
        validation_alias=AliasChoices("BOT_ID", "MicrosoftAppId", "APP_ID")
    )
    APP_PASSWORD: SecretStr = Field(
        validation_alias=AliasChoices(
            "BOT_PASSWORD", 
            "SECRET_BOT_PASSWORD", 
            "MicrosoftAppPassword", 
            "APP_PASSWORD"
        )
    )
    APP_TYPE: str = Field(
        default="SingleTenant",
        validation_alias=AliasChoices("BOT_TYPE", "APP_TYPE", "MicrosoftAppType")
    )
    TENANT_ID: str = Field(
        default="",
        validation_alias=AliasChoices("TEAMS_APP_TENANT_ID", "MicrosoftAppTenantId", "TENANT_ID")
    )
    
    model_config = SettingsConfigDict(
        env_file=[ENV_DIR / ".env", ENV_DIR / ".env.local"],
        env_ignore_empty=True,
        extra="ignore"
    )


class AIConfig(BaseSettings):
    """
    Universal AI configuration class.
    Replaces OpenAI-specific config with a vendor-agnostic approach.
    """
    AI_PROVIDER: AIProvider = Field(
        default=AIProvider.OPENAI,
        description="AI service provider (openai, gemini, ollama, anthropic)"
    )
    AI_MODEL_NAME: str = Field(
        validation_alias=AliasChoices("AI_MODEL_NAME", "OPENAI_MODEL_NAME"),
        description="Name of the AI model to use"
    )
    AI_API_KEY: Optional[SecretStr] = Field(
        default=None,
        validation_alias=AliasChoices("AI_API_KEY", "OPENAI_API_KEY"),
        description="API Key for the AI provider"
    )
    AI_BASE_URL: Optional[str] = Field(
        default=None,
        description="Base URL for local models (Ollama/vLLM) or proxy"
    )
    AI_API_VERSION: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("AI_API_VERSION"),
        description="API version for the AI provider if applicable"
    )
    AI_MAX_RETRIES: int = Field(
        default=2, 
        description="Maximum number of retries for AI API calls"
    )
    AI_RETRY_DELAY: float = Field(
        default=1.0, 
        description="Delay between AI retry attempts in seconds"
    )
    
    model_config = SettingsConfigDict(
        env_file=[
            ENV_DIR / ".env",
            ENV_DIR / ".env.local",
            ENV_DIR / ".env.local.user",
        ],
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True
    )
    
    @model_validator(mode="after")
    def validate_credentials(self):
        """Ensure required credentials are provided based on AI provider"""
        # Cloud providers that strictly require an API Key
        cloud_providers = AIProvider.cloud_providers()
        
        if self.AI_PROVIDER in cloud_providers and not self.AI_API_KEY:
            raise ValueError(f"AI_API_KEY is required for {self.AI_PROVIDER}")
        return self


class EmailConfig(BaseSettings):
    """Email service configuration (Azure Communication Services)"""
    
    COMMUNICATION_CONNECTION_STRING: Optional[SecretStr] = None
    MAIL_FROM_ADDRESS: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=[ENV_DIR / ".env", ENV_DIR / ".env.local"],
        env_ignore_empty=True,
        extra="ignore"
    )


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    
    DB_PATH: str = Field(default="time_off.db")
    
    DB_HOST: Optional[str] = None
    DB_PORT: int = Field(default=5432)
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[SecretStr] = None
    
    @property
    def database_url(self) -> str:
        """Generate SQLAlchemy connection string"""
        if self.DB_HOST and self.DB_NAME and self.DB_USER:
            pwd = self.DB_PASSWORD.get_secret_value() if self.DB_PASSWORD else ""
            return f"postgresql+asyncpg://{self.DB_USER}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"sqlite+aiosqlite:///{self.DB_PATH}"
    
    model_config = SettingsConfigDict(
        env_file=[ENV_DIR / ".env", ENV_DIR / ".env.local"],
        env_ignore_empty=True,
        extra="ignore"
    )


class AppConfig(BaseSettings):
    """General application configuration"""
    
    PROJECT_NAME: str = Field(default="HR Bot")
    PROJECT_DESCRIPTION: str = Field(default="HR Onboarding Assistant Bot")
    PROJECT_VERSION: str = Field(default="1.0.0")
    PORT: int = Field(default=3978)
    DEFAULT_LICENSE_SKU_ID: str = Field(default="")
    
    model_config = SettingsConfigDict(
        env_file=[ENV_DIR / ".env", ENV_DIR / ".env.local"],
        env_ignore_empty=True,
        extra="ignore"
    )


class DevConfig(BaseSettings):
    """Development and testing configuration"""
    
    TEST_USER_ID: Optional[str] = None
    DEFAULT_APPROVER: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=[ENV_DIR / ".env", ENV_DIR / ".env.local"],
        env_ignore_empty=True,
        extra="ignore"
    )


# --- Main Configuration Class (Facade) ---

class Config:
    """
    Main application configuration facade.
    Combines all sections and provides backward compatibility.
    """
    
    def __init__(self):
        self.azure_bot = AzureBotConfig()
        self.ai = AIConfig()
        self.email = EmailConfig()
        self.database = DatabaseConfig()
        self.app = AppConfig()
        self.dev = DevConfig()
    
    # --- Backward Compatibility Properties ---
    
    @property
    def APP_ID(self) -> str:
        return self.azure_bot.APP_ID
    
    @property
    def APP_PASSWORD(self) -> str:
        return self.azure_bot.APP_PASSWORD.get_secret_value()
    
    @property
    def APP_TYPE(self) -> str:
        return self.azure_bot.APP_TYPE
    
    @property
    def TENANT_ID(self) -> str:
        return self.azure_bot.TENANT_ID
    
    @property
    def AI_API_KEY(self) -> str:
        return self.ai.AI_API_KEY.get_secret_value() if self.ai.AI_API_KEY else ""

    # Legacy alias for OpenAI-specific code
    @property
    def OPENAI_API_KEY(self) -> str:
        return self.AI_API_KEY
    
    @property
    def AI_PROVIDER(self) -> AIProvider:
        return self.ai.AI_PROVIDER
    
    @property
    def AI_API_BASE_URL(self) -> Optional[str]:
        return self.ai.AI_BASE_URL
    
    @property
    def AI_MODEL_NAME(self) -> str:
        return self.ai.AI_MODEL_NAME
    
    @property
    def AI_API_VERSION(self) -> Optional[str]:
        return self.ai.AI_API_VERSION

    # Legacy alias for OpenAI-specific code
    @property
    def OPENAI_MODEL_NAME(self) -> str:
        return self.AI_MODEL_NAME
    
    @property
    def database_url(self) -> str:
        return self.database.database_url
    
    @property
    def PORT(self) -> int:
        return self.app.PORT
    
    @property
    def AI_MAX_RETRIES(self) -> int:
        return self.ai.AI_MAX_RETRIES
    
    @property
    def AI_RETRY_DELAY_SECONDS(self) -> float:
        return self.ai.AI_RETRY_DELAY

    @property
    def COMMUNICATION_CONNECTION_STRING(self) -> Optional[str]:
        """Email Connection String (backward compatibility)"""
        if self.email.COMMUNICATION_CONNECTION_STRING:
            return self.email.COMMUNICATION_CONNECTION_STRING.get_secret_value()
        return None
    
    @property
    def MAIL_FROM_ADDRESS(self) -> Optional[str]:
        """Email From Address (backward compatibility)"""
        return self.email.MAIL_FROM_ADDRESS

    @property
    def DB_PATH(self) -> str:
        """Database Path (backward compatibility)"""
        return self.database.DB_PATH

    @property
    def PROJECT_NAME(self) -> str:
        """Project Name (backward compatibility)"""
        return self.app.PROJECT_NAME

    @property
    def DEFAULT_LICENSE_SKU_ID(self) -> str:
        """License SKU ID (backward compatibility)"""
        return self.app.DEFAULT_LICENSE_SKU_ID
    
    @property
    def TEST_USER_ID(self) -> Optional[str]:
        """Test User ID (backward compatibility)"""
        return self.dev.TEST_USER_ID
    
    @property
    def DEFAULT_APPROVER(self) -> Optional[str]:
        """Default Approver (backward compatibility)"""
        return self.dev.DEFAULT_APPROVER
    
    @property
    def PROJECT_VERSION(self) -> str:
        """Project Version (backward compatibility)"""
        return self.app.PROJECT_VERSION
    
    @property
    def PROJECT_DESCRIPTION(self) -> str:
        """Project Description (backward compatibility)"""
        return self.app.PROJECT_DESCRIPTION

# --- Singleton Instance ---
settings = Config()


def log_settings():
    """Safe logging of configuration."""
    bot_pwd = settings.APP_PASSWORD
    masked_pwd = f"{bot_pwd[:3]}***" if bot_pwd else "❌ EMPTY"
    
    logger.info("\n🔧 CONFIGURATION LOADED (Universal AI Mode):")
    logger.info(f"   🤖 Bot ID: {settings.APP_ID}")
    logger.info(f"   🔑 Bot Secret: {masked_pwd}")
    logger.info(f"   🧠 AI Provider: {settings.ai.AI_PROVIDER.value}")
    logger.info(f"   🧠 AI Model: {settings.AI_MODEL_NAME}")
    logger.info(f"   🗄️  DB URL: {settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database.DB_PATH}")
    logger.info("-" * 30)

