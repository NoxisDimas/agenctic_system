import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.config.settings import settings
from app.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, priority: int = 1):
        super().__init__(name="openai", priority=priority)
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = settings.OPENAI_MODEL or "gpt-3.5-turbo"

    def get_llm(self, **kwargs):
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model_name,
            **kwargs
        )

    def check_health(self, timeout: float = 2.0) -> bool:
        if not self.api_key:
            return False
        try:
            llm = self.get_llm(request_timeout=timeout, max_retries=0)
            llm.invoke([HumanMessage(content="ping")])
            return True
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False
