from typing import Any, Dict
from app.channels.core.base_adapter import BaseChannelAdapter
from app.channels.core.models import InternalMessage, InternalResponse, ChannelType

class WebAdapter(BaseChannelAdapter):
    def from_request(self, raw_request: Dict[str, Any]) -> InternalMessage:
        # Assuming raw_request is a dict from JSON body
        return InternalMessage(
            user_id=raw_request.get("user_id", "anonymous"),
            channel=ChannelType.WEB,
            text=raw_request.get("text", ""),
            metadata=raw_request.get("metadata", {})
        )

    def to_response(self, internal_response: InternalResponse) -> Dict[str, Any]:
        return {
            "text": internal_response.text,
            "metadata": internal_response.metadata,
            "rich_content": internal_response.rich_content
        }
