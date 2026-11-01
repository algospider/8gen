"""LLM provider factory."""

from eightgen.config.settings import Settings
from eightgen.llm.base import LLMProvider
from eightgen.llm.ollama import OllamaProvider
from eightgen.llm.gemini import GeminiProvider
from eightgen.utils.logger import get_logger

logger = get_logger("eightgen.llm.factory")


def create_llm_provider(settings: Settings) -> LLMProvider:
    """Create appropriate LLM provider based on settings and available keys."""
    # Priority 1: Gemini if provider is gemini or GEMINI_API_KEY is present
    if settings.provider.lower() in ("gemini", "google") or settings.gemini_api_key or settings.gemini_proxy_url:
        logger.info(f"Using Gemini Provider (Model: {settings.gemini_model})")
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
            proxy_url=settings.gemini_proxy_url,
            timeout=settings.timeout,
        )

    # Priority 2: Ollama provider
    logger.info(f"Using local Ollama Provider (Model: {settings.model})")
    return OllamaProvider(
        base_url=settings.ollama_url,
        model=settings.model,
        timeout=settings.timeout,
    )
