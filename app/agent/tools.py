import logging
from typing import Optional, Type, List, Callable, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool, StructuredTool

from app.services.lightrag import LightRAGClient
from app.memory.controller import MemoryController

logger = logging.getLogger(__name__)

class ToolWrapper(BaseModel):
    name: str
    description: str
    func: Callable
    args_schema: Optional[Type[BaseModel]] = None

    def wrap_tool(self) -> BaseTool:
        return StructuredTool.from_function(
            func=self.func,
            name=self.name,
            description=self.description,
            args_schema=self.args_schema
        )

# --- Tool Arguments Schemas ---

class SearchInput(BaseModel):
    query: str = Field(description="The search query to look up in the knowledge base.")

class UserIDInput(BaseModel):
    user_id: str = Field(description="The unique identifier of the user.")

class SavePreferenceInput(BaseModel):
    user_id: str = Field(description="The unique identifier of the user.")
    preference: str = Field(description="The preference or fact to save about the user.")

# --- Tool Implementations ---

def create_search_tool(client: LightRAGClient):
    async def search_knowledge(query: str) -> str:
        """Search the knowledge base (FAQ, documentation, etc.) for answers."""
        try:
            # We can use 'hybrid' or 'global' mode
            return await client.query(query, mode="hybrid")
        except Exception as e:
            logger.error(f"Error searching Knowledge Base: {e}")
            return "Error accessing knowledge base."
    return search_knowledge

def create_read_profile_tool(controller: MemoryController):
    def read_profile(user_id: str) -> str:
        """Read the summary of the user's profile and history."""
        return controller.summarize_user_context(user_id)
    return read_profile

def create_save_pref_tool(controller: MemoryController):
    def save_pref(user_id: str, preference: str) -> str:
        """Save a user preference or important fact to memory."""
        controller.add_memory(user_id, preference, type="preference")
        return "Preference saved successfully."
    return save_pref

# --- Registry ---

def get_tools(rag_client: LightRAGClient, memory_ctrl: MemoryController) -> List[ToolWrapper]:
    return [
        ToolWrapper(
            name="search_knowledge_base",
            description="Search the comprehensive knowledge base (FAQ, docs, policies).",
            func=create_search_tool(rag_client),
            args_schema=SearchInput
        ),
        ToolWrapper(
            name="read_profile",
            description="Read the user's profile context (history, preferences).",
            func=create_read_profile_tool(memory_ctrl),
            args_schema=UserIDInput
        ),
        ToolWrapper(
            name="save_preference",
            description="Save a new preference or fact about the user for future reference.",
            func=create_save_pref_tool(memory_ctrl),
            args_schema=SavePreferenceInput
        )
    ]
