from typing import Union, Optional, Any

from pydantic import BaseModel, Field, ConfigDict

from core.enums.bot import (
    BotModule,
    BotRequestType,
    get_module_for_action,
    get_module_for_intent,
)

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
    
    @property
    def module(self) -> Optional[str]:
        """
        Returns the module associated with the request based on its type.
        """
        if self.request_type == BotRequestType.ACTION:
            return get_module_for_action(self.payload.action)
        elif self.request_type == BotRequestType.INTENT:
            return get_module_for_intent(self.payload.intent)
        
        return BotModule.GENERAL
    
    
__all__ = (
    "ClassifiedRequest",
)

