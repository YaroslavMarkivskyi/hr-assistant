import logging  
import json
from typing import Any, Dict

from botbuilder.core import TurnContext
from botbuilder.schema import Activity, ActivityTypes, Attachment


logger = logging.getLogger(__name__)

class ActivityContextWrapper:
    """
    Wrapper that adapts TurnContext to ActivityContext API.
    
    This allows existing code that expects ActivityContext to work
    with Bot Framework's TurnContext.
    """
    
    def __init__(self, turn_context: TurnContext):
        """
        Initialize wrapper with TurnContext.
        
        Args:
            turn_context: Bot Framework TurnContext
        """
        self._turn_context = turn_context
        self.activity = turn_context.activity
    
    @property
    def text(self) -> str:
        return self.activity.text or ""
    
    async def send_activity(self, text: str) -> None:
        """
        Send a message to the user (alias for send, for compatibility).
        
        Args:
            text: Message text to send
        """
        await self._turn_context.send_activity(text)
    
    async def send_typing_activity(self) -> None:
        """
        Send typing indicator to show user that bot is processing.
        
        This creates a typing activity and sends it through TurnContext.
        """
        typing_activity = Activity(
            type=ActivityTypes.typing,
            channel_id=self.activity.channel_id,
            conversation=self.activity.conversation,
            recipient=self.activity.from_property
        )
        await self._turn_context.send_activity(typing_activity)
    
    async def send_adaptive_card(self, card_data: Dict[str, Any]) -> None:
        """
        Sends an Adaptive Card to the user.
        Includes safety mechanisms to ensure JSON validity.
        """
        try:
            if isinstance(card_data, str):
                try:
                    card_data = json.loads(card_data)
                except json.JSONDecodeError:
                    logger.error("send_adaptive_card received invalid JSON string")
                    return

            sanitized_content = json.loads(json.dumps(card_data, default=str))

            attachment = Attachment(
                content_type="application/vnd.microsoft.card.adaptive",
                content=sanitized_content 
            )
            message = Activity(
                type=ActivityTypes.message,
                attachments=[attachment]
            )

            await self._turn_context.send_activity(message)
            
        except Exception as e:
            logger.error(f"Failed to send adaptive card: {e}", exc_info=True)
            # TODO: Add localized user-friendly error message
            await self._turn_context.send_activity("Sorry, I couldn't display the card at this time.")

    def __getattr__(self, name: str) -> Any:
        """
        Delegate unknown attributes to TurnContext.
        This allows access to TurnContext methods/properties
        that aren't explicitly defined in the wrapper.
        """
        return getattr(self._turn_context, name)
    
    
__all__ = ("ActivityContextWrapper",)

