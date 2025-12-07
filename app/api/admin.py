from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from langchain_core.documents import Document

from app.api import deps
from app.api import deps
from app.services.lightrag import LightRAGClient


router = APIRouter()

class IngestRequest(BaseModel):
    text: str
    description: Optional[str] = None
    
class SearchRequest(BaseModel):
    query: str
    mode: str = "hybrid"

@router.post("/lightrag/ingest")
async def ingest_text(
    request: IngestRequest,
    client: LightRAGClient = Depends(deps.get_lightrag_client)
):
    """Admin endpoint to ingest text into LightRAG."""
    try:
        res = await client.insert_text(request.text, description=request.description)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lightrag/search")
async def search_documents(
    request: SearchRequest,
    client: LightRAGClient = Depends(deps.get_lightrag_client)
):
    """Admin endpoint to search LightRAG."""
    try:
        result = await client.query(request.query, mode=request.mode)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
