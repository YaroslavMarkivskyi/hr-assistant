"""
Main application entry point
"""
import asyncio
from typing import Any

from azure.identity import ManagedIdentityCredential
from botbuilder.core import MemoryStorage
from microsoft.teams.apps import App, ActivityContext

from config import Config
from container import ServiceContainer
from bot.router import MessageRouter

# Initialize configuration
config = Config()

# --- INITIALIZATION ---
def create_token_factory():
    """Creates token factory for Azure authentication"""
    def get_token(scopes, tenant_id=None):
        credential = ManagedIdentityCredential(client_id=config.APP_ID)
        token = credential.get_token(*(scopes if not isinstance(scopes, str) else [scopes]))
        return token.token
    return get_token

storage = MemoryStorage()

app = App(
    token=create_token_factory() if config.APP_TYPE == "UserAssignedMsi" else None,
    storage=storage
)

# Create service container
service_container = ServiceContainer.create(config)

# --- MESSAGE HANDLER ---
@app.on_message
async def handle_message(ctx: ActivityContext, state: Any = None):
    """
    Main message handler - delegates to router
    
    Args:
        ctx: Activity context from Teams
        state: Optional state (not used currently)
    """
    router = MessageRouter(ctx, service_container)
    await router.route()

if __name__ == "__main__":
    asyncio.run(app.start())
