"""
FastAPI Routes

Contains all FastAPI endpoints for the bot.
Uses FastAPI Dependency Injection pattern via request.app.state.

This approach:
- Loose coupling: routes don't depend on BotContainer import
- FastAPI idiomatic: uses request.app.state for global resources
- Easy testing: can inject mock objects in tests
"""
import logging
import os
from typing import TYPE_CHECKING
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from botbuilder.schema import Activity
from botbuilder.core import TurnContext

if TYPE_CHECKING:
    from core.containers.bot_container import BotContainer

logger = logging.getLogger("HRBot")

# Check if we're in development mode
IS_DEVELOPMENT = os.getenv(
    "ENVIRONMENT", 
    "production"
    ).lower() in (
        "development", 
        "dev", 
        "local"
        )

# Global router instance (FastAPI idiomatic approach)
router = APIRouter()


def _create_error_response(
    error_message: str,
    error_type: str,
    error_details: str | None = None
) -> dict:
    """
    Create error response dictionary.
    
    In development mode, includes error details and type for debugging.
    In production mode, only includes the error message for security.
    
    Args:
        error_message: User-friendly error message
        error_type: Type of the error (e.g., "ValueError", "ConnectionError")
        error_details: Optional detailed error information
        
    Returns:
        Dictionary with error response
    """
    response = {"error": error_message}
    
    if IS_DEVELOPMENT:
        if error_details:
            response["details"] = error_details
        response["type"] = error_type
    
    return response


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


@router.post("/api/messages")
async def messages(request: Request):
    """
    Teams Bot Framework endpoint.
    
    Handles incoming messages from Microsoft Teams.
    Uses Dependency Injection via request.app.state to access bot infrastructure.
    """
    # Validate content type
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        logger.warning(f"❌ Invalid content type: {content_type}")
        return Response(
            status_code=415, 
            content="Content-Type must be application/json"
            )
    
    try:
        # Get bot container from app state (FastAPI Dependency Injection)
        # Type hint for IDE autocomplete and static type checking
        bot_container: "BotContainer" = request.app.state.bot_container
        
        # Validate that bot_container is available
        if not bot_container:
            logger.error("❌ BotContainer not found in app.state")
            return JSONResponse(
                status_code=503,
                content={"error": "Service unavailable"}
            )
        
        # Parse request body
        body = await request.json()
        activity = Activity.deserialize(body)
        auth_header = request.headers.get("Authorization", "")
        
        # Turn handler function for bot processing
        # This wrapper allows for future extensions (logging, metrics, error handling)
        async def handle_turn(turn_context: TurnContext) -> None:
            """
            Handler function for processing bot turns.
            
            This explicit function provides a place for:
            - Logging turn start/end
            - Performance metrics
            - Error interception at business logic level
            """
            await bot_container.bot.on_turn(turn_context)
        
        # Process activity with bot logic
        await bot_container.adapter.process_activity(
            activity, 
            auth_header, 
            handle_turn
        )
        
        return JSONResponse(status_code=200, content={})
        
    except ValueError as e:
        # Invalid request data (malformed JSON, missing fields, etc.)
        logger.warning(f"⚠️ Invalid request data: {e}")
        return JSONResponse(
            status_code=400,
            content=_create_error_response(
                "Invalid request data", 
                "ValueError", 
                str(e)
            )
        )
    
    except KeyError as e:
        # Missing required fields in request
        logger.warning(f"⚠️ Missing required field: {e}")
        return JSONResponse(
            status_code=400,
            content=_create_error_response(
                "Missing required field in request",
                "KeyError",
                f"Missing field: {str(e)}"
            )
        )
    
    except ConnectionError as e:
        # Network/connection issues (database, external APIs)
        logger.error(f"❌ Connection error: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content=_create_error_response(
                "Service temporarily unavailable",
                "ConnectionError",
                str(e)
            )
        )
    
    except TimeoutError as e:
        # Request timeout
        logger.error(f"⏱️ Timeout error: {e}", exc_info=True)
        return JSONResponse(
            status_code=504,
            content=_create_error_response(
                "Request timeout", 
                "TimeoutError", 
                str(e)
                )
        )
    
    except AttributeError as e:
        # Missing attributes (e.g., bot_container not properly initialized)
        logger.error(f"❌ Attribute error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=_create_error_response(
                "Service configuration error",
                "AttributeError",
                str(e)
            )
        )
    
    except Exception as e:
        # Catch-all for any other unexpected errors
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=_create_error_response(
                "Internal server error",
                type(e).__name__,
                str(e)
            )
        )

