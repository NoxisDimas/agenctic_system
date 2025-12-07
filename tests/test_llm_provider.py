import pytest
from app.llm.openai_provider import OpenAIProvider
from app.llm.groq_provider import GroqProvider

def test_openai_provider_initialization():
    provider = OpenAIProvider()
    assert provider.name == "openai"
    assert provider.priority == 1
    # Check if get_llm returns an object (mocking might be needed for full check without API key)
    # Here we just check instantiation logic
    assert provider.get_llm() is not None

def test_groq_provider_initialization():
    provider = GroqProvider()
    assert provider.name == "groq"
    assert provider.priority == 2
