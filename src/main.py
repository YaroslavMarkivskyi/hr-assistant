"""
FastAPI Application Entry Point

Clean entry point that assembles all components using Composition Root pattern:
- ServiceContainer: Business services (Graph, DB, OpenAI, Email)
- BotContainer: Bot infrastructure (Adapter, State, Bot Instance)
- FastAPI app with routes

Uses modern FastAPI patterns:
- lifespan context manager (replaces deprecated @app.on_event)
- APIRouter for modular route management
- Separation of concerns via containers
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from api.routes import router
from container import ServiceContainer
from bot.container import BotContainer
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HRBot")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application.
    
    Manages startup and shutdown logic in a single place.
    This replaces the deprecated @app.on_event("startup") and @app.on_event("shutdown").
    
    Uses Composition Root pattern:
    1. Create ServiceContainer (business services)
    2. Create BotContainer (bot infrastructure)
    3. Register routes
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("🚀 Initializing application...")
    
    # 1. Create ServiceContainer (business services)
    service_container = ServiceContainer.create(settings)
    logger.info("✅ ServiceContainer initialized")
    
    # 2. Create BotContainer (bot infrastructure)
    bot_container = BotContainer.create(service_container)
    
    # 3. Store containers in app state (for Dependency Injection in routes)
    app.state.service_container = service_container
    app.state.bot_container = bot_container
    
    # 4. Register routes (router uses request.app.state for DI)
    app.include_router(router)
    
    logger.info("✅ FastAPI application started")
    logger.info(f"📋 Bot ID: {settings.APP_ID}")
    logger.info(f"🏢 Tenant ID: {settings.TENANT_ID}")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("🛑 FastAPI application shutting down")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="HR Assistant Bot",
    description="Microsoft Teams Bot for HR operations",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "running",
        "version": "1.0.0",
        "service": "HR Assistant Bot"
    }
