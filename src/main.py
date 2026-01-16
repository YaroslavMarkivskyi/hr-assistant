import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from api.routes import router
from container import ServiceContainer
from bot.container import BotContainer
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("🚀 Initializing application...")
    
    service_container = ServiceContainer.create(settings)
    logger.info("✅ ServiceContainer initialized")
    
    bot_container = BotContainer.create(service_container)
    
    app.state.service_container = service_container
    app.state.bot_container = bot_container
    
    
    logger.info("✅ FastAPI application started")
    logger.info(f"📋 Bot ID: {settings.APP_ID}")
    logger.info(f"🏢 Tenant ID: {settings.TENANT_ID}")
    
    yield
    logger.info("🛑 FastAPI application shutting down")


app = FastAPI(
    title="HR Assistant Bot",
    description="Microsoft Teams Bot for HR operations",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "status": "running",
        "version": "1.0.0",
        "service": "HR Assistant Bot"
    }

