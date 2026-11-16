from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelInfo:
    """Information about a model discovered from a provider."""

    id: str
    display_name: str
    capabilities: set[str] = field(default_factory=set)
    context_window: int | None = None
    supports_structured_output: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationRequest:
    """Standard request sent to any LLM provider."""

    system_prompt: str
    user_prompt: str
    temperature: float = 0.2
    max_output_tokens: int | None = None
    response_schema: dict[str, Any] | None = None


@dataclass
class GenerationResult:
    """Standardized response returned by any LLM provider."""

    content: str
    provider: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str | None = None


class ProviderError(Exception):
    """Base exception for provider-related failures."""


class RateLimitError(ProviderError):
    """Raised when a provider rate limit is reached."""


class AuthenticationError(ProviderError):
    """Raised when provider authentication fails."""


class ModelUnavailableError(ProviderError):
    """Raised when a requested model is unavailable."""


class TemporaryProviderError(ProviderError):
    """Raised when a provider has a temporary failure."""


class BaseProvider(ABC):
    """Common interface that every LLM provider must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider's unique identifier."""
        pass

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Check whether the provider has the required credentials."""
        pass

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        """Discover models available through this provider."""
        pass

    @abstractmethod
    async def generate(
        self,
        model_id: str,
        request: GenerationRequest
    ) -> GenerationResult:
        """Generate a response using the selected model."""
        pass    

    