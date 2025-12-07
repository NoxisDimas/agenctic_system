from abc import ABC, abstractmethod
from typing import Any, Optional
from langchain_core.language_models.chat_models import BaseChatModel

class BaseLLMProvider(ABC):
    def __init__(self, name: str, priority: int):
        self.name = name
        self.priority = priority

    @abstractmethod
    def get_llm(self, **kwargs) -> BaseChatModel:
        """Return a LangChain ChatModel instance."""
        pass

    @abstractmethod
    def check_health(self, timeout: float = 2.0) -> bool:
        """Check if the provider is healthy."""
        pass
