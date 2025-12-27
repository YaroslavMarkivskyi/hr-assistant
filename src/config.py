import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# --- 1. Визначаємо шляхи до папки env ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
secret_env_path = os.path.join(base_dir, "env", ".env.local.user")
public_env_path = os.path.join(base_dir, "env", ".env.local")

# --- 2. Явно завантажуємо змінні в оточення ---
# Спочатку секрети (паролі), потім публічні ID
load_dotenv(secret_env_path)
load_dotenv(public_env_path)
load_dotenv() # На випадок, якщо є звичайний .env

class Config(BaseSettings):
    """
    Configuration class to load environment variables.
    """
    PORT: int = 3978
    
    # Pydantic візьме ці значення з os.environ, який ми наповнили вище
    APP_ID: str = os.environ.get("BOT_ID", os.environ.get("CLIENT_ID", ""))
    
    # Шукаємо пароль у всіх можливих варіантах, які створює Teams Toolkit
    APP_PASSWORD: str = os.environ.get("BOT_PASSWORD", os.environ.get("SECRET_BOT_PASSWORD", ""))
    
    APP_TYPE: str = os.environ.get("BOT_TYPE", "UserAssignedMsi")
    TENANT_ID: str = os.environ.get("TEAMS_APP_TENANT_ID", "")
    
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME: str = os.environ.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
    
    COMMUNICATION_CONNECTION_STRING: str = os.environ.get("COMMUNICATION_CONNECTION_STRING", "")
    MAIL_FROM_ADDRESS: str = os.environ.get("MAIL_FROM_ADDRESS", "")
    
    # Ліцензія для призначення новим користувачам (SKU ID)
    # Приклад: "f30db892-07e9-47e9-837c-80727f46fd3d" для Microsoft 365 Business Basic
    DEFAULT_LICENSE_SKU_ID: str = os.environ.get("DEFAULT_LICENSE_SKU_ID", "")
    
    # Тестовий ID користувача для локального тестування (якщо requester_id не знайдено з activity)
    # Встановіть це значення в .env для локального тестування
    TEST_USER_ID: str = os.environ.get("TEST_USER_ID", "")

    class Config:
        # Ми вже завантажили файли вручну, тому тут можна залишити стандартний .env
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# --- 3. Діагностика (щоб ти бачив у терміналі, чи підтягнувся пароль) ---
try:
    cfg = Config()
    masked_pwd = f"{cfg.APP_PASSWORD[:3]}***" if cfg.APP_PASSWORD else "❌ EMPTY"
    license_status = cfg.DEFAULT_LICENSE_SKU_ID if cfg.DEFAULT_LICENSE_SKU_ID else "❌ NOT SET"
    print(f"\n🔧 CONFIG DIAGNOSTIC:")
    print(f"   BOT_ID: {cfg.APP_ID}")
    print(f"   BOT_PASSWORD: {masked_pwd}")
    print(f"   TENANT_ID: {cfg.TENANT_ID}")
    print(f"   DEFAULT_LICENSE_SKU_ID: {license_status}\n")
except Exception as e:
    print(f"❌ Config Error: {e}")