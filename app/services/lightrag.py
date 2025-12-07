import httpx
import logging
from typing import Optional, List, Dict, Any
from app.config.settings import settings

logger = logging.getLogger(__name__)

class LightRAGClient:
    def __init__(self, base_url: str = "http://lightrag:9621"):
        self.base_url = base_url.rstrip("/")

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error requesting {url}: {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Error communicating with LightRAG: {e}")
                raise

    async def check_health(self) -> bool:
        try:
            # Assuming a health endpoint exists or root returns 200
            await self._request("GET", "/health") 
            return True
        except:
            return False

    async def insert_text(self, text: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Insert raw text into LightRAG."""
        payload = {"text": text}
        if description:
            payload["description"] = description
        return await self._request("POST", "/insert/text", json=payload)

    async def insert_file(self, file_path: str) -> Dict[str, Any]:
        """
        Insert a file. 
        Note: If LightRAG is in Docker and this client is in another Docker, 
        'file_path' must be accessible to LightRAG or uploaded via multipart.
        For now, assuming multipart upload if API supports it, or path if shared volume.
        Standard LightRAG API usually takes text or file paths if local.
        Since we are in different containers, we should probably upload content as text
        or rely on shared volume.
        Let's implement text insertion primarily for now, or check if /insert/file accepts uploads.
        """
        # Placeholder for file upload logic if API supports it
        raise NotImplementedError("File upload not fully verified. Use insert_text.")

    async def query(self, query: str, mode: str = "global") -> str:
        """
        Query LightRAG.
        modes: 'global', 'local', 'hybrid', 'naive'
        """
        payload = {
            "query": query,
            "mode": mode
        }
        response = await self._request("POST", "/query", json=payload)
        # Response format depends on LightRAG version.
        # usually {"response": "answer..."}
        if isinstance(response, dict) and "response" in response:
            return response["response"]
        return str(response)

# Singleton instance
lightrag_client = LightRAGClient(base_url=getattr(settings, "LIGHTRAG_API_URL", "http://lightrag:9621"))
