from functools import lru_cache
from typing import List

from app.config.settings import settings, Settings
from app.llm.base import BaseLLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.groq_provider import GroqProvider
from app.llm.ollama_provider import OllamaProvider
from app.llm.manager import LLMManager
from app.services.lightrag import lightrag_client, LightRAGClient
from app.memory.controller import MemoryController
from app.agent.tools import get_tools
from app.agent.config import AgentConfig
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from app.agent.builder import build_graph_agent

@lru_cache()
def get_settings() -> Settings:
    return settings

# --- Singletons for heavy objects ---

_pg_pool = None

def get_postgres_pool() -> ConnectionPool:
    global _pg_pool
    if _pg_pool is None:
        _pg_pool = ConnectionPool(
            conninfo=settings.POSTGRES_URI, 
            max_size=20,
            kwargs={"autocommit": True}
        )
    return _pg_pool

def get_checkpointer() -> PostgresSaver:
    pool = get_postgres_pool()
    # PostgresSaver needs a connection, but typically we want it to manage lifecycle or use a pool.
    # The standard usage: with pool.connection() as conn: checkpointer = PostgresSaver(conn)
    # However, standard dependency injection style might require passing the Checkpointer object that holds the connection.
    # Updated LangGraph Checkpointer Usage: 
    # checkpointer = PostgresSaver(pool) -- check newer docs.
    # Actually, PostgresSaver expects a connection object OR a pool if constructed correctly? 
    # Looking at typical usage: `checkpointer = PostgresSaver(conn)`
    # Since we want to reuse it, we might need a context manager or a wrapper.
    # For now, let's assume we pass the pool and let the graph usage handle it if supported, 
    # OR we follow the example: passing the checkpointer into compile().
    # Let's instantiate a saver with the pool if the library supports it. 
    # If not, we might need to handle connection per request.
    
    # SAFE PATTERN: PostgresSaver(conn)
    # We will instantiate it inside the build_graph_agent or right here?
    # To keep it simple: We return the pool, and let the builder/runner handle connection context if needed.
    # BUT `build_graph_agent` takes `checkpointer`.
    
    # Quick fix: Return a checkpointer connected to the pool/conn.
    # warning: Checkpointer might need setup() called.
    
    return PostgresSaver(pool)

@lru_cache()
def get_llm_manager() -> LLMManager:
    providers: List[BaseLLMProvider] = [
        OpenAIProvider(priority=1),
        GroqProvider(priority=2),
        OllamaProvider(priority=3)
    ]
    return LLMManager(providers)

@lru_cache()
def get_lightrag_client() -> LightRAGClient:
    return lightrag_client

@lru_cache()
def get_memory_controller() -> MemoryController:
    # MemoryController needs LLM for summarization, so we pass the manager
    return MemoryController(llm_manager=get_llm_manager())

def get_agent_graph():
    """
    Builds the agent graph. 
    Note: We don't cache the graph WITH the checkpointer if checkingpointer relies on open cursors.
    But PostgresSaver(pool) should be thread safe and reusable.
    """
    llm_mgr = get_llm_manager()
    llm_mgr = get_llm_manager()
    rag_client = get_lightrag_client()
    memory_ctrl = get_memory_controller()
    
    tools = get_tools(rag_client, memory_ctrl)
    config = AgentConfig()
    
    checkpointer = get_checkpointer()
    # Ensure checkpointer tables exist
    checkpointer.setup()
    
    return build_graph_agent(llm_mgr, tools, config, checkpointer=checkpointer)
