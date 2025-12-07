from typing import Any, Dict
from app.channels.core.base_adapter import BaseChannelAdapter
from app.channels.core.models import InternalMessage, InternalResponse, ChannelType

class TelegramAdapter(BaseChannelAdapter):
    def from_request(self, raw_request: Dict[str, Any]) -> InternalMessage:
        # Placeholder for Telegram webhook payload
        message = raw_request.get("message", {})
        user_id = str(message.get("from", {}).get("id", "unknown_tg"))
        text = message.get("text", "")
        
        return InternalMessage(
            user_id=user_id,
            channel=ChannelType.TELEGRAM,
            text=text,
            metadata=raw_request
        )

    def to_response(self, internal_response: InternalResponse) -> Dict[str, Any]:
        # Return format for Telegram (usually we'd call an API directly, 
        # but here we return a dict description or webhook response)
        return {
            "method": "sendMessage",
            "text": internal_response.text,
            "parse_mode": "Markdown"
        }
