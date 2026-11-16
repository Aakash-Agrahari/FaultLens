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