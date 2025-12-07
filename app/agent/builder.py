import logging
from typing import List, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

from app.llm.manager import LLMManager
from app.agent.tools import ToolWrapper
from app.agent.config import AgentConfig
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Global pool for sync connections (if needed) or simple connection string usage
# PostgresSaver usually takes a sync connection or pool.
# For simplicity with FastApi dependencies, we might initialize it per request or global.
# We'll creating a helper to get the checkpointer.

def build_graph_agent(
    llm_manager: LLMManager,
    tools: List[ToolWrapper],
    config: AgentConfig,
    checkpointer: Optional[PostgresSaver] = None
):
    """
    Builds and returns a LangGraph ReAct agent.
    """
    # 1. Get LLM
    llm = llm_manager.get_llm(temperature=0)
    
    # 2. Convert tools
    lc_tools: List[BaseTool] = [t.wrap_tool() for t in tools]
    
    # 3. Create ReAct Agent (LangGraph prebuilt)
    # The system prompt is passed via state_modifier or messages.
    # create_react_agent handles the graph construction.
    
    graph = create_react_agent(
        model=llm,
        tools=lc_tools,
        prompt=config.system_prompt,
        checkpointer=checkpointer
    )
    
    return graph
