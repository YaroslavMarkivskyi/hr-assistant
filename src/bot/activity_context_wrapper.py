"""
ActivityContext Wrapper

Adapts Bot Framework TurnContext to ActivityContext API.
This allows existing router and handlers to work with TurnContext.
"""
import logging  
import json
from typing import Any, Union, Dict
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
        """Get message text (for compatibility)"""
        return self.activity.text or ""
    
    async def send(self, message: Union[str, Any]) -> None:
        """
        Send a message to the user.
        
        Supports:
        - Plain text (str)
        - MessageActivityInput (from microsoft.teams.api) with Adaptive Cards
        
        Args:
            message: Message text (str) or MessageActivityInput object
        """
        # Handle MessageActivityInput (Adaptive Cards)
        if hasattr(message, 'type') and hasattr(message, 'attachments'):
            # Get attachments - ensure it's a list, not tuple
            attachments_list = message.attachments
            if isinstance(attachments_list, tuple):
                attachments_list = list(attachments_list)
            elif not isinstance(attachments_list, list):
                attachments_list = []
            
            # Convert MessageActivityInput to Bot Framework Activity
            # Ensure all attachment data is properly formatted
            activity_attachments = []
            for att in attachments_list:
                try:
                    # Handle both dict and object access
                    if isinstance(att, dict):
                        content_type = att.get("contentType", "")
                        content = att.get("content", {})
                    else:
                        # Object with attributes
                        content_type = getattr(att, "contentType", getattr(att, "content_type", ""))
                        content = getattr(att, "content", {})
                    
                    # Ensure content is a dict, not tuple or other type
                    if not isinstance(content, dict):
                        continue
                    
                    # Ensure content_type is a string (not tuple)
                    content_type_str = str(content_type) if content_type else "application/vnd.microsoft.card.adaptive"
                    
                    # Bot Framework SDK expects content to be a dict for Adaptive Cards
                    # The SDK will serialize it to JSON automatically
                    # But we need to ensure it's a clean dict (no tuples, no non-serializable objects)
                    try:
                        # Recursively clean the content dict to ensure JSON serializability
                        def _clean_for_json(obj):
                            """Recursively clean object for JSON serialization"""
                            if isinstance(obj, dict):
                                return {str(k): _clean_for_json(v) for k, v in obj.items()}
                            elif isinstance(obj, (list, tuple)):
                                return [_clean_for_json(item) for item in obj]
                            elif isinstance(obj, (str, int, float, bool)) or obj is None:
                                return obj
                            else:
                                # Convert other types to string
                                return str(obj)
                        
                        cleaned_content = _clean_for_json(content)
                        
                        # Verify it can be serialized
                        json.dumps(cleaned_content)
                        
                    except (TypeError, ValueError) as e:
                        # Skip if content cannot be serialized
                        import logging
                        logger = logging.getLogger("HRBot")
                        logger.warning(f"⚠️ Cannot serialize attachment content: {e}")
                        continue
                    
                    activity_attachments.append(
                        Attachment(
                            content_type=content_type_str,
                            content=cleaned_content  # Pass dict, SDK will serialize
                        )
                    )
                except (AttributeError, TypeError) as e:
                    # Skip invalid attachments
                    import logging
                    logger = logging.getLogger("HRBot")
                    logger.warning(f"⚠️ Skipping invalid attachment: {e}")
                    continue
            
            # Create Activity with only necessary fields to avoid serialization issues
            activity = Activity(
                type=ActivityTypes.message,
                attachments=activity_attachments if activity_attachments else None
            )
            await self._turn_context.send_activity(activity)
        else:
            # Plain text message
            await self._turn_context.send_activity(str(message))
    
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
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate unknown attributes to TurnContext.
        This allows access to TurnContext methods/properties
        that aren't explicitly defined in the wrapper.
        """
        return getattr(self._turn_context, name)

    async def send_adaptive_card(self, card_data: Dict[str, Any]) -> None:
        """
        Sends an Adaptive Card to the user.
        Includes safety mechanisms to ensure JSON validity.
        """
        try:
            # 1. SAFETY CHECK: Якщо раптом прийшов рядок, перетворимо в dict
            if isinstance(card_data, str):
                try:
                    card_data = json.loads(card_data)
                except json.JSONDecodeError:
                    logger.error("❌ send_adaptive_card received invalid JSON string")
                    return

            # 2. SANITIZATION: "Ядерне" очищення. 
            # json.dumps з default=str перетворить всі datetime/uuid/custom об'єкти в рядки.
            # json.loads поверне нам чисту структуру з примітивів, яку точно прийме SDK.
            sanitized_content = json.loads(json.dumps(card_data, default=str))

            # 3. Create Attachment
            attachment = Attachment(
                content_type="application/vnd.microsoft.card.adaptive",
                content=sanitized_content 
            )

            # 4. Create Message
            message = Activity(
                type=ActivityTypes.message,
                attachments=[attachment]
            )

            # 5. Send
            await self._turn_context.send_activity(message)
            
        except Exception as e:
            logger.error(f"❌ Failed to send adaptive card: {e}", exc_info=True)
            # Фолбек: відправити хоча б текст помилки, щоб юзер не чекав вічно
            await self._turn_context.send_activity("Вибачте, сталася технічна помилка при відображенні картки.")

    def __getattr__(self, name: str) -> Any:
        return getattr(self._turn_context, name)
    