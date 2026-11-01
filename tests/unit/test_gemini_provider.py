"""Unit tests for Gemini Provider."""

import pytest
from eightgen.llm.gemini import GeminiProvider
from eightgen.llm.base import LLMMessage


def test_gemini_message_conversion():
    provider = GeminiProvider(api_key="test-key")
    messages = [
        LLMMessage(role="system", content="You are a game maker."),
        LLMMessage(role="user", content="Make space invaders."),
    ]
    payload = provider._convert_messages_for_gemini(messages)
    assert "systemInstruction" in payload
    assert payload["systemInstruction"]["parts"][0]["text"] == "You are a game maker."
    assert len(payload["contents"]) == 1
    assert payload["contents"][0]["role"] == "user"
    assert payload["contents"][0]["parts"][0]["text"] == "Make space invaders."


@pytest.mark.asyncio
async def test_gemini_no_key_error():
    provider = GeminiProvider(api_key="")
    messages = [LLMMessage(role="user", content="hi")]
    with pytest.raises(ValueError, match="Gemini API key is required"):
        await provider.generate(messages)
