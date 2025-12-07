import logging
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from app.config.settings import settings
from app.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class OllamaProvider(BaseLLMProvider):
    def __init__(self, priority: int = 3):
        super().__init__(name="ollama", priority=priority)
        self.base_url = settings.OLLAMA_BASE_URL
        self.model_name = settings.OLLAMA_MODEL

    def get_llm(self, **kwargs):
        return ChatOllama(
            base_url=self.base_url,
            model=self.model_name,
            **kwargs
        )

    def check_health(self, timeout: float = 2.0) -> bool:
        try:
            # Use a very short timeout for health check
            # Note: ChatOllama might accept 'timeout' in seconds
            llm = self.get_llm(timeout=timeout)
            llm.invoke([HumanMessage(content="ping")])
            return True
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
