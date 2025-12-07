import logging
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage
from app.channels.core.models import InternalMessage, InternalResponse

logger = logging.getLogger(__name__)

async def run_agent(
    graph,
    message: InternalMessage,
    session_context: Optional[Dict[str, Any]] = None
) -> InternalResponse:
    """
    Run the agent graph with the given message.
    """
    try:
        # LangChain v1: Use proper message objects instead of tuples
        # The agent expects "messages" key with proper message objects
        human_message = HumanMessage(content=message.text)
        inputs = {"messages": [human_message]}
        
        # Config for checkpointing
        # session_context usually contains user_id/thread_id
        # We map user_id to thread_id for simple 1-to-1 mapping, or use specific thread_id
        user_id = message.user_id
        thread_id = session_context.get("thread_id", user_id) if session_context else user_id
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke graph 
        # For remote/sync checkpointer, invoke is synchronous usually unless using async checkpointer
        # Since we use PostgresSaver (sync), we use invoke.
        
        # However, for async fastapi, blocking the loop is bad.
        # Let's wrap in to_thread since `graph.invoke` with sync checkpointer is blocking.
        import asyncio
        result = await asyncio.to_thread(graph.invoke, inputs, config)
        
        # Result state contains 'messages'
        messages = result.get("messages", [])
        last_message = messages[-1] if messages else None
        # In LangChain v1, use .text property instead of .text() method
        output_text = last_message.text if last_message and hasattr(last_message, 'text') else (
            last_message.content if last_message else "No response generated."
        )
        
        return InternalResponse(
            text=str(output_text),
            metadata={
                "agent_name": "CustomerServiceAgent (LangGraph)", 
                "thread_id": thread_id
            }
        )
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        return InternalResponse(
            text="I apologize, but I encountered an internal error. Please try again later.",
            metadata={"error": str(e)}
        )
