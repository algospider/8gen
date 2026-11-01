"""Google Gemini API and Gemini-compatible proxy provider."""

import json
from typing import AsyncGenerator, Dict, List, Optional, Any
import httpx

from eightgen.llm.base import LLMMessage, LLMProvider, LLMResponse
from eightgen.utils.logger import get_logger

logger = get_logger("eightgen.gemini")

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(LLMProvider):
    """Provider for Google Gemini API or local OpenAI-compatible Gemini proxy."""

    def __init__(
        self,
        api_key: str = "",
        model: str = "gemini-2.5-flash",
        proxy_url: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.api_key = api_key.strip()
        self.model = model or "gemini-2.5-flash"
        self.proxy_url = proxy_url.rstrip("/") if proxy_url else None
        self.timeout = timeout

    async def is_healthy(self) -> bool:
        """Check if Gemini API or Proxy is reachable."""
        if self.proxy_url:
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    res = await client.get(f"{self.proxy_url}/models")
                    return res.status_code == 200
            except Exception:
                return False

        if not self.api_key:
            return False

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{GEMINI_API_BASE}/models?key={self.api_key}")
                return res.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """List available models."""
        if self.proxy_url:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    res = await client.get(f"{self.proxy_url}/models")
                    if res.status_code == 200:
                        data = res.json().get("data", [])
                        return [m.get("id") for m in data if m.get("id")]
            except Exception:
                pass
            return ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-flash"]

        return [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]

    def _convert_messages_for_gemini(self, messages: List[LLMMessage]) -> Dict[str, Any]:
        """Convert standard messages to Gemini contents format."""
        system_instruction = None
        contents = []

        for msg in messages:
            if msg.role == "system":
                system_instruction = {"parts": [{"text": msg.content}]}
            elif msg.role in ("user", "assistant"):
                role = "user" if msg.role == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg.content}]})

        payload: Dict[str, Any] = {"contents": contents}
        if system_instruction:
            payload["systemInstruction"] = system_instruction
        return payload

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate complete response via Gemini API or Proxy."""
        if self.proxy_url:
            return await self._generate_via_proxy(messages, temperature, **kwargs)

        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. Set GEMINI_API_KEY in your environment or .env file."
            )

        gemini_payload = self._convert_messages_for_gemini(messages)
        gemini_payload["generationConfig"] = {
            "temperature": temperature,
            "maxOutputTokens": 8192,
        }

        # Normalize model name
        model_name = self.model
        if model_name.startswith("models/"):
            model_name = model_name.replace("models/", "")

        url = f"{GEMINI_API_BASE}/models/{model_name}:generateContent?key={self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, json=gemini_payload)
                if res.status_code != 200:
                    err_msg = res.text
                    try:
                        err_json = res.json()
                        err_msg = err_json.get("error", {}).get("message", res.text)
                    except Exception:
                        pass
                    raise RuntimeError(f"Gemini API error ({res.status_code}): {err_msg}")

                data = res.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise RuntimeError("No candidates returned by Gemini.")

                parts = candidates[0].get("content", {}).get("parts", [])
                content = "".join([p.get("text", "") for p in parts])

                usage = data.get("usageMetadata", {})
                return LLMResponse(
                    content=content,
                    model=model_name,
                    prompt_tokens=usage.get("promptTokenCount"),
                    completion_tokens=usage.get("candidatesTokenCount"),
                    raw=data,
                )
        except httpx.ConnectError:
            raise ConnectionError("Cannot connect to Google Gemini API servers.")

    async def stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream chunks via Gemini API or Proxy."""
        if self.proxy_url:
            async for chunk in self._stream_via_proxy(messages, temperature, **kwargs):
                yield chunk
            return

        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. Set GEMINI_API_KEY in your environment or .env file."
            )

        gemini_payload = self._convert_messages_for_gemini(messages)
        gemini_payload["generationConfig"] = {
            "temperature": temperature,
            "maxOutputTokens": 8192,
        }

        model_name = self.model.replace("models/", "")
        url = f"{GEMINI_API_BASE}/models/{model_name}:streamGenerateContent?alt=sse&key={self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, json=gemini_payload) as response:
                    if response.status_code != 200:
                        err_body = await response.aread()
                        raise RuntimeError(f"Gemini API streaming error ({response.status_code}): {err_body.decode()}")

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        json_str = line[len("data:"):].strip()
                        if not json_str:
                            continue
                        try:
                            data = json.loads(json_str)
                            candidates = data.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                for p in parts:
                                    text = p.get("text", "")
                                    if text:
                                        yield text
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            raise ConnectionError("Cannot connect to Google Gemini API servers.")

    async def _generate_via_proxy(
        self, messages: List[LLMMessage], temperature: float, **kwargs: Any
    ) -> LLMResponse:
        """Call OpenAI-compatible proxy (e.g. oorja proxy)."""
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": False,
        }
        headers = {"Authorization": f"Bearer {self.api_key or 'not-needed'}"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.post(f"{self.proxy_url}/chat/completions", json=payload, headers=headers)
            if res.status_code != 200:
                raise RuntimeError(f"Proxy error ({res.status_code}): {res.text}")
            data = res.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return LLMResponse(content=content, model=self.model, raw=data)

    async def _stream_via_proxy(
        self, messages: List[LLMMessage], temperature: float, **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": True,
        }
        headers = {"Authorization": f"Bearer {self.api_key or 'not-needed'}"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", f"{self.proxy_url}/chat/completions", json=payload, headers=headers) as res:
                if res.status_code != 200:
                    err = await res.aread()
                    raise RuntimeError(f"Proxy streaming error: {err.decode()}")
                async for line in res.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    chunk_raw = line[len("data:"):].strip()
                    if chunk_raw == "[DONE]":
                        break
                    try:
                        delta = json.loads(chunk_raw).get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            yield delta
                    except Exception:
                        continue
