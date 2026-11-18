from dataclasses import dataclass
from datetime import datetime, timezone

from app.ai.providers.base import (
    ProviderError,
    RateLimitError,
    AuthenticationError,
    ModelUnavailableError,
    TemporaryProviderError
)


@dataclass
class ModelHealth:
    provider: str
    model_id: str

    status: str = "unknown"

    consecutive_failures: int = 0

    last_success_at: datetime | None = None
    last_failure_at: datetime | None = None

    last_error: str | None = None


class ProviderHealthTracker:

    def __init__(self):

        self._health: dict[tuple[str, str], ModelHealth] = {}

    def _get_or_create(
        self,
        provider: str,
        model_id: str
    ) -> ModelHealth:

        key = (provider, model_id)

        if key not in self._health:
            self._health[key] = ModelHealth(
                provider=provider,
                model_id=model_id
            )

        return self._health[key]

    def record_success(
        self,
        provider: str,
        model_id: str
    ):

        health = self._get_or_create(provider, model_id)

        health.status = "healthy"
        health.consecutive_failures = 0
        health.last_success_at = datetime.now(timezone.utc)
        health.last_error = None

    def record_failure(
        self,
        provider: str,
        model_id: str,
        error: Exception
    ):

        health = self._get_or_create(provider, model_id)

        health.consecutive_failures += 1
        health.last_failure_at = datetime.now(timezone.utc)
        health.last_error = str(error)

        if isinstance(error, RateLimitError):
            health.status = "rate_limited"

        elif isinstance(error, AuthenticationError):
            health.status = "authentication_error"

        elif isinstance(error, ModelUnavailableError):
            health.status = "model_unavailable"

        elif isinstance(error, TemporaryProviderError):
            health.status = "temporarily_unavailable"

        elif isinstance(error, ProviderError):
            health.status = "provider_error"

        else:
            health.status = "unknown_error"

    def get_health(
        self,
        provider: str,
        model_id: str
    ) -> ModelHealth:

        return self._get_or_create(provider, model_id)

    def get_all_health(self) -> list[ModelHealth]:

        return list(self._health.values())
