import logging
from typing import Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Path


from app.config.settings import settings
from app.api import deps
from app.api import admin
from app.channels.core.models import ChannelType
from app.channels.web.adapter import WebAdapter
from app.channels.whatsapp.adapter import WhatsAppAdapter
from app.channels.telegram.adapter import TelegramAdapter
from app.agent.runner import run_agent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.AGENT_NAME,
    version="0.1.0"
)

app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Adapters
adapters = {
    ChannelType.WEB: WebAdapter(),
    ChannelType.WHATSAPP: WhatsAppAdapter(),
    ChannelType.TELEGRAM: TelegramAdapter(),
}

@app.get("/health")
def health_check(
    llm_manager=Depends(deps.get_llm_manager),
    # qdrant=Depends(deps.get_qdrant_controller) # Check connection if needed
):
    """Health check endpoint."""
    llm_status = llm_manager.check_all_providers()
    return {
        "status": "ok",
        "llm_providers": llm_status,
        "environment": settings.ENVIRONMENT
    }

@app.post("/v1/chat/{channel_name}")
async def chat_endpoint(
    channel_name: ChannelType,
    payload: Dict[str, Any],
    graph = Depends(deps.get_agent_graph)
):
    """
    Unified chat endpoint for all channels.
    """
    if channel_name not in adapters:
         raise HTTPException(status_code=400, detail=f"Unsupported channel: {channel_name}")
    
    adapter = adapters[channel_name]
    
    # 1. Adapt Request
    try:
        internal_msg = adapter.from_request(payload)
    except Exception as e:
        logger.error(f"Error parsing request for {channel_name}: {e}")
        raise HTTPException(status_code=400, detail="Invalid request format")

    # 2. Run Agent
    # Note: run_agent is async wrapper
    try:
        internal_response = await run_agent(graph, internal_msg)
    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        raise HTTPException(status_code=500, detail="Internal agent error")
    
    # 3. Adapt Response
    return adapter.to_response(internal_response)
