from __future__ import annotations
import logging
import os
from typing import TYPE_CHECKING

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from botbuilder.schema import Activity
from botbuilder.core import TurnContext


if TYPE_CHECKING:
    from core.containers.bot_container import BotContainer


logger = logging.getLogger(__name__)


IS_DEVELOPMENT = os.getenv(
    "ENVIRONMENT", 
    "production"
    ).lower() in (
        "development", 
        "dev", 
        "local"
        )

router = APIRouter()


def _create_error_response(
    error_message: str,
    error_type: str,
    error_details: str | None = None
) -> dict:
    response = {"error": error_message}
    
    if IS_DEVELOPMENT:
        if error_details:
            response["details"] = error_details
        response["type"] = error_type
    
    return response


@router.post("/messages")
async def messages(request: Request):
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        logger.warning(f"Invalid content type: {content_type}")
        return Response(
            status_code=415, 
            content="Content-Type must be application/json"
            )
    
    try:
        bot_container: BotContainer = request.app.state.bot_container
        
        if not bot_container:
            logger.error("BotContainer not found in app.state")
            return JSONResponse(
                status_code=503,
                content={"error": "Service unavailable"}
            )
        
        body = await request.json()
        activity = Activity.deserialize(body)
        auth_header = request.headers.get("Authorization", "")
        
        async def handle_turn(turn_context: TurnContext) -> None:
            await bot_container.bot.on_turn(turn_context)
        
        await bot_container.adapter.process_activity(
            activity, 
            auth_header, 
            handle_turn
        )
        
        return JSONResponse(status_code=200, content={})
        
    except ValueError as e:
        logger.warning(f"Invalid request data: {e}")
        return JSONResponse(
            status_code=400,
            content=_create_error_response(
                "Invalid request data", 
                "ValueError", 
                str(e)
            )
        )
    
    except KeyError as e:
        logger.warning(f"Missing required field: {e}")
        return JSONResponse(
            status_code=400,
            content=_create_error_response(
                "Missing required field in request",
                "KeyError",
                f"Missing field: {str(e)}"
            )
        )
    
    except ConnectionError as e:
        logger.error(f"Connection error: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content=_create_error_response(
                "Service temporarily unavailable",
                "ConnectionError",
                str(e)
            )
        )
    
    except TimeoutError as e:
        logger.error(f"Timeout error: {e}", exc_info=True)
        return JSONResponse(
            status_code=504,
            content=_create_error_response(
                "Request timeout", 
                "TimeoutError", 
                str(e)
                )
        )
    
    except AttributeError as e:
        logger.error(f"Attribute error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=_create_error_response(
                "Service configuration error",
                "AttributeError",
                str(e)
            )
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=_create_error_response(
                "Internal server error",
                type(e).__name__,
                str(e)
            )
        )

