"""
Application Configuration Module

Organized into logical configuration classes for better maintainability.
Refactored for Single Tenant Azure Bot support.
"""
from typing import Optional
from pathlib import Path
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_DIR = BASE_DIR / "env"


# --- Configuration Classes ---

class AzureBotConfig(BaseSettings):
    """Azure Bot Framework configuration"""
    
    APP_ID: str = Field(
        validation_alias=AliasChoices("BOT_ID", "MicrosoftAppId", "APP_ID")
    )
    APP_PASSWORD: str = Field(
        validation_alias=AliasChoices(
            "BOT_PASSWORD", 
            "SECRET_BOT_PASSWORD", 
            "MicrosoftAppPassword", 
            "APP_PASSWORD"
        )
    )
    # ЗМІНЕНО: Default is now SingleTenant. Added MicrosoftAppType alias.
    APP_TYPE: str = Field(
        default="SingleTenant",
        validation_alias=AliasChoices("BOT_TYPE", "APP_TYPE", "MicrosoftAppType")
    )
    # ЗМІНЕНО: Added MicrosoftAppTenantId and TENANT_ID aliases.
    TENANT_ID: str = Field(
        default="",
        validation_alias=AliasChoices("TEAMS_APP_TENANT_ID", "MicrosoftAppTenantId", "TENANT_ID")
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


class OpenAIConfig(BaseSettings):
    """OpenAI service configuration"""
    
    OPENAI_API_KEY: str
    OPENAI_MODEL_NAME: str = Field(default="gpt-3.5-turbo")
    
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


class EmailConfig(BaseSettings):
    """Email service configuration (Azure Communication Services)"""
    
    COMMUNICATION_CONNECTION_STRING: Optional[str] = None
    MAIL_FROM_ADDRESS: Optional[str] = None
    
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


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    
    # SQLite (default for local dev)
    DB_PATH: str = Field(default="time_off.db")
    
    # PostgreSQL (for production/Docker)
    DB_HOST: Optional[str] = None
    DB_PORT: int = Field(default=5432)
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    
    @property
    def database_url(self) -> str:
        """Generate SQLAlchemy connection string"""
        # Use PostgreSQL if credentials are provided
        if self.DB_HOST and self.DB_NAME and self.DB_USER and self.DB_PASSWORD:
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        # Otherwise use SQLite
        return f"sqlite+aiosqlite:///{self.DB_PATH}"
    
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


class AppConfig(BaseSettings):
    """General application configuration"""
    
    PROJECT_NAME: str = Field(default="HR Bot")
    PORT: int = Field(default=3978)
    DEFAULT_LICENSE_SKU_ID: str = Field(default="")
    
    # AI Retry Configuration
    AI_MAX_RETRIES: int = Field(default=2, description="Maximum number of retries for AI API calls")
    AI_RETRY_DELAY_SECONDS: float = Field(default=1.0, description="Delay between AI retry attempts in seconds")
    
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


class DevConfig(BaseSettings):
    """Development and testing configuration"""
    
    TEST_USER_ID: Optional[str] = None
    DEFAULT_APPROVER: Optional[str] = None
    
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


# --- Main Configuration Class ---

class Config:
    """
    Main application configuration.
    
    Combines all configuration sections for easy access.
    Maintains backward compatibility with flat attribute access.
    """
    
    def __init__(self):
        """Initialize Config by loading nested configs from environment."""
        # Load each nested config from environment
        self.azure_bot = AzureBotConfig()
        self.openai = OpenAIConfig()
        self.email = EmailConfig()
        self.database = DatabaseConfig()
        self.app = AppConfig()
        self.dev = DevConfig()
    
    # --- Backward Compatibility: Flat Access ---
    # These properties allow existing code to access config.APP_ID, config.DB_PATH, etc.
    
    @property
    def APP_ID(self) -> str:
        """Azure Bot App ID (backward compatibility)"""
        return self.azure_bot.APP_ID
    
    @property
    def APP_PASSWORD(self) -> str:
        """Azure Bot App Password (backward compatibility)"""
        return self.azure_bot.APP_PASSWORD
    
    @property
    def APP_TYPE(self) -> str:
        """Azure Bot App Type (backward compatibility)"""
        return self.azure_bot.APP_TYPE
    
    @property
    def TENANT_ID(self) -> str:
        """Azure Tenant ID (backward compatibility)"""
        return self.azure_bot.TENANT_ID
    
    @property
    def OPENAI_API_KEY(self) -> str:
        """OpenAI API Key (backward compatibility)"""
        return self.openai.OPENAI_API_KEY
    
    @property
    def OPENAI_MODEL_NAME(self) -> str:
        """OpenAI Model Name (backward compatibility)"""
        return self.openai.OPENAI_MODEL_NAME
    
    @property
    def COMMUNICATION_CONNECTION_STRING(self) -> Optional[str]:
        """Email Communication Connection String (backward compatibility)"""
        return self.email.COMMUNICATION_CONNECTION_STRING
    
    @property
    def MAIL_FROM_ADDRESS(self) -> Optional[str]:
        """Email From Address (backward compatibility)"""
        return self.email.MAIL_FROM_ADDRESS
    
    @property
    def DB_PATH(self) -> str:
        """Database Path (backward compatibility)"""
        return self.database.DB_PATH
    
    @property
    def database_url(self) -> str:
        """Database URL (backward compatibility)"""
        return self.database.database_url
    
    @property
    def PROJECT_NAME(self) -> str:
        """Project Name (backward compatibility)"""
        return self.app.PROJECT_NAME
    
    @property
    def PORT(self) -> int:
        """Application Port (backward compatibility)"""
        return self.app.PORT
    
    @property
    def DEFAULT_LICENSE_SKU_ID(self) -> str:
        """Default License SKU ID (backward compatibility)"""
        return self.app.DEFAULT_LICENSE_SKU_ID
    
    @property
    def TEST_USER_ID(self) -> Optional[str]:
        """Test User ID (backward compatibility)"""
        return self.dev.TEST_USER_ID
    
    @property
    def DEFAULT_APPROVER(self) -> Optional[str]:
        """Default Approver ID (backward compatibility)"""
        return self.dev.DEFAULT_APPROVER
    
    @property
    def AI_MAX_RETRIES(self) -> int:
        """AI Max Retries (backward compatibility)"""
        return self.app.AI_MAX_RETRIES
    
    @property
    def AI_RETRY_DELAY_SECONDS(self) -> float:
        """AI Retry Delay Seconds (backward compatibility)"""
        return self.app.AI_RETRY_DELAY_SECONDS


# --- Singleton Instance ---
settings = Config()


# --- Logging Function ---
def log_settings():
    """Log configuration settings (called from main.py, not on import)"""
    masked_pwd = f"{settings.APP_PASSWORD[:3]}***" if settings.APP_PASSWORD else "❌ EMPTY"
    
    print("\n🔧 CONFIGURATION LOADED:")
    print(f"   📂 Env Dir: {ENV_DIR}")
    print(f"   🤖 Bot ID: {settings.APP_ID}")
    print(f"   🔑 Password: {masked_pwd}")
    print(f"   🏢 Tenant ID: {settings.TENANT_ID or '❌ Not set'}")
    print(f"   ⚙️  App Type: {settings.APP_TYPE}")
    print(f"   🗄️  DB URL: {settings.database_url}")
    print("-" * 30)