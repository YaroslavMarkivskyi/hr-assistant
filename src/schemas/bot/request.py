from typing import Union, Optional, Any

from pydantic import BaseModel, Field, ConfigDict

from core.enums.bot import BotRequestType

from .payloads import ActionPayload, IntentPayload


class ClassifiedRequest(BaseModel):
    """
    Represents a classified bot request with its type and payload.
    """
    request_type: BotRequestType = Field(
        ..., 
        description="The type of the bot request (action or intent)."
        )
    payload: Union[ActionPayload, IntentPayload] = Field(
        ...,
        description="The payload of the bot request."
        )
    raw_data: Optional[str] = Field(
        None,
        description="Optional raw data associated with the request."
        )
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    
__all__ = (
    "ClassifiedRequest",
)

