"""Integration test for OllamaProvider against local Ollama instance."""

import pytest
from eightgen.llm.ollama import OllamaProvider


@pytest.mark.asyncio
async def test_ollama_connectivity():
    provider = OllamaProvider(base_url="http://localhost:11434")
    is_healthy = await provider.is_healthy()
    assert is_healthy is True, "Ollama must be reachable on http://localhost:11434"

    models = await provider.list_models()
    assert len(models) > 0, "At least one model should be downloaded in Ollama"

    resolved = await provider.resolve_model()
    assert resolved != ""
