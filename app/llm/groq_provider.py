import logging
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from app.config.settings import settings
from app.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class GroqProvider(BaseLLMProvider):
    def __init__(self, priority: int = 2):
        super().__init__(name="groq", priority=priority)
        self.api_key = settings.GROQ_API_KEY
        self.model_name = settings.GROQ_MODEL

    def get_llm(self, **kwargs):
        # ChatGroq might not support request_timeout in constructor in some versions,
        # but typically it does or via transport options.
        # We'll pass kwargs directly.
        return ChatGroq(
            api_key=self.api_key,
            model_name=self.model_name,
            **kwargs
        )

    def check_health(self, timeout: float = 2.0) -> bool:
        if not self.api_key:
            return False
        try:
            # Groq implementation of invoke
            llm = self.get_llm(request_timeout=timeout, max_retries=0)
            llm.invoke([HumanMessage(content="ping")])
            return True
        except Exception as e:
            logger.warning(f"Groq health check failed: {e}")
            return False
