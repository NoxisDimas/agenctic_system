from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import field_validator
class Settings(BaseSettings):
    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str) and v == "":
            return None
        return v
    # Environment
    ENVIRONMENT: Literal["dev", "prod"] = "dev"
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = "gpt-3.5-turbo"
    
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: Optional[str] = "llama3-70b-8192"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: Optional[str] = "llama3"
    
    # LLM Manager Configuration
    LLM_MODE: Literal["static", "auto"] = "auto"
    LLM_STATIC_PROVIDER: Optional[str] = "openai"
    
    # Qdrant Settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    # If using local Qdrant memory/disk mode without server
    QDRANT_PATH: Optional[str] = None 

    # Mem0 Settings
    MEM0_API_KEY: Optional[str] = None
    
    # Postgres (Checkpointer)
    POSTGRES_URI: str = "postgresql://postgres:postgres@localhost:5432/agent_db"

    # Agent
    AGENT_NAME: str = "CustomerServiceAgent"
    
    # LightRAG
    LIGHTRAG_API_URL: str = "http://lightrag:9621"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
