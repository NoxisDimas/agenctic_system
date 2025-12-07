import pytest
from app.channels.web.adapter import WebAdapter
from app.channels.core.models import ChannelType, InternalResponse

def test_web_adapter():
    adapter = WebAdapter()
    
    # From Request
    req = {"user_id": "u1", "text": "hello", "metadata": {"foo": "bar"}}
    msg = adapter.from_request(req)
    assert msg.channel == ChannelType.WEB
    assert msg.user_id == "u1"
    assert msg.text == "hello"
    
    # To Response
    resp = InternalResponse(text="hi", metadata={"latency": "1ms"})
    final_resp = adapter.to_response(resp)
    assert final_resp["text"] == "hi"
    assert final_resp["metadata"]["latency"] == "1ms"
