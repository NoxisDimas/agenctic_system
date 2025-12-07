import logging
from typing import List, Optional, Dict, Literal
from app.llm.base import BaseLLMProvider
from app.config.settings import settings

logger = logging.getLogger(__name__)

class LLMError(Exception):
    """Custom exception for LLM related errors."""
    pass

class LLMManager:
    def __init__(self, providers: List[BaseLLMProvider]):
        self.providers = sorted(providers, key=lambda p: p.priority)
        self.mode = settings.LLM_MODE
        self.static_provider_name = settings.LLM_STATIC_PROVIDER

    def get_llm(self, **kwargs):
        """
        Get an LLM instance based on the configuration mode.
        """
        if self.mode == "static":
            return self._get_static_provider(**kwargs)
        else:
            return self._get_auto_provider(**kwargs)

    def _get_static_provider(self, **kwargs):
        provider = next((p for p in self.providers if p.name == self.static_provider_name), None)
        if not provider:
             raise LLMError(f"Static provider '{self.static_provider_name}' not found.")
        logger.info(f"Using static LLM provider: {provider.name}")
        return provider.get_llm(**kwargs)

    def _get_auto_provider(self, **kwargs):
        # Iterate through providers by priority
        for provider in self.providers:
            if provider.check_health():
                logger.info(f"Selected healthy LLM provider: {provider.name}")
                return provider.get_llm(**kwargs)
        
        # If no provider is healthy
        raise LLMError("No healthy LLM providers available.")

    def check_all_providers(self) -> Dict[str, bool]:
        """Check health of all providers."""
        status = {}
        for provider in self.providers:
            is_healthy = provider.check_health()
            status[provider.name] = is_healthy
        return status
