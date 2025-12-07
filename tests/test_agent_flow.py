import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.agent.runner import run_agent
from app.channels.core.models import InternalMessage, ChannelType

@pytest.mark.asyncio
async def test_run_agent_flow():
    # Mock Graph
    mock_graph = MagicMock()
    # run_agent uses asyncio.to_thread(graph.invoke, ...)
    # The return value of invoke is a dict with "messages"
    mock_message = MagicMock()
    mock_message.content = "Agent response"
    mock_response = {"messages": [mock_message]}
    
    mock_graph.invoke.return_value = mock_response
    
    msg = InternalMessage(
        user_id="u1",
        channel=ChannelType.WEB,
        text="Hello"
    )
    
    response = await run_agent(mock_graph, msg)
    
    assert response.text == "Agent response"
    assert response.metadata["agent_name"] == "CustomerServiceAgent (LangGraph)"
    mock_graph.invoke.assert_called_once()
