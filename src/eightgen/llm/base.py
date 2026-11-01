"""Abstract base classes for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncGenerator, Dict, List, Optional, Any


@dataclass
class LLMMessage:
    """A chat message."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Full LLM response."""
    content: str
    model: str
    total_duration_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate complete response."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks asynchronously."""
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available models."""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if provider is running and reachable."""
        pass
