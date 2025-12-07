import logging
from typing import List, Optional, Union, Dict
from mem0 import Memory
from app.config.settings import settings
from app.memory.models import MemoryItem

logger = logging.getLogger(__name__)

class MemoryController:
    def __init__(self, llm_manager=None):
        # We don't necessarily need llm_manager directly if mem0 handles it, 
        # but we might keep the signature for compatibility or custom config.
        # Mem0 config:
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "host": settings.QDRANT_HOST,
                    "port": settings.QDRANT_PORT,
                    "api_key": settings.QDRANT_API_KEY,
                    "path": settings.QDRANT_PATH
                }
            }
        }
        # If using hosted mem0, we might just pass api_key
        # For now, assuming local usage with Qdrant as backend per project stack
        
        try:
            if settings.MEM0_API_KEY:
                # Hosted mode or specific config
                 self.memory = Memory(api_key=settings.MEM0_API_KEY)
            else:
                 # Local mode with custom vector store config
                 self.memory = Memory.from_config(config)
        except Exception as e:
            logger.warning(f"Failed to initialize Mem0 with config, falling back to default: {e}")
            self.memory = Memory()

    def get_memory(self, user_id: str, *, types: Optional[List[str]] = None) -> List[MemoryItem]:
        """
        Retrieve memories for a user.
        'types' filtering might need to be handled via metadata filtering if mem0 supports it,
        or client-side filtering.
        """
        try:
            memories = self.memory.get_all(user_id=user_id)
            items = []
            for m in memories:
                # Mem0 returns dicts, need to parse to MemoryItem
                # Structure roughly: {'id': '...', 'memory': '...', 'user_id': '...', 'metadata': {...}}
                item = MemoryItem(**m)
                
                # Filter by 'type' if stored in metadata
                if types:
                    item_type = item.metadata.get("type")
                    if item_type not in types:
                        continue
                items.append(item)
            return items
        except Exception as e:
            logger.error(f"Error getting memory for {user_id}: {e}")
            return []

    def add_memory(self, user_id: str, data: Union[str, dict], *, type: str, tags: Optional[List[str]] = None) -> MemoryItem:
        """
        Add a memory item.
        """
        try:
            metadata = {"type": type}
            if tags:
                metadata["tags"] = tags
            
            # mem0.add expects 'messages' or text. 
            # If using 'add', it processes and stores factual memories.
            result = self.memory.add(data, user_id=user_id, metadata=metadata)
            
            # Result is typically a list of added memories or the added item
            # We'll just return the first one as a MemoryItem for consistency
            if isinstance(result, list) and result:
                return MemoryItem(**result[0])
            elif isinstance(result, dict):
                 return MemoryItem(**result)
            
            # Fallback if no return
            return MemoryItem(id="unknown", user_id=user_id, memory=str(data), metadata=metadata)

        except Exception as e:
            logger.error(f"Error adding memory for {user_id}: {e}")
            raise e

    def clear_memory(self, user_id: str, *, types: Optional[List[str]] = None) -> None:
        """
        Clear memories. Mem0 typically supports delete(memory_id) or delete_all(user_id).
        """
        try:
            if types:
                # If clearing strict types, we must fetch then delete by ID
                items = self.get_memory(user_id, types=types)
                for item in items:
                    self.memory.delete(item.id)
            else:
                self.memory.delete_all(user_id=user_id)
        except Exception as e:
            logger.error(f"Error clearing memory for {user_id}: {e}")

    def summarize_user_context(self, user_id: str) -> str:
        """
        Mem0 often does not have a direct 'summarize this user' function public yet 
        (it does internal graph usually), so we might fetch all and summarize, 
        or rely on its search.
        """
        items = self.get_memory(user_id)
        if not items:
            return "User has no previous history/context."
        
        context_str = "\n".join([f"- {item.content} (Type: {item.metadata.get('type','general')})" for item in items])
        return f"User Context (Mem0):\n{context_str}"
