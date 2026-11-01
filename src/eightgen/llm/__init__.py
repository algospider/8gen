"""LLM integration layer for 8Gen."""

from eightgen.llm.base import LLMMessage, LLMResponse, LLMProvider
from eightgen.llm.ollama import OllamaProvider
from eightgen.llm.gemini import GeminiProvider
from eightgen.llm.factory import create_llm_provider
from eightgen.llm.prompt_builder import PromptBuilder
from eightgen.llm.models import ModelInfo

__all__ = [
    "LLMMessage",
    "LLMResponse",
    "LLMProvider",
    "OllamaProvider",
    "GeminiProvider",
    "create_llm_provider",
    "PromptBuilder",
    "ModelInfo",
]
