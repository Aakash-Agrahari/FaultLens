
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from app.ai.providers.base import RateLimitError


@dataclass
class RateLimitState:

    provider: str
    model_id: str

    rate_limit_observed: bool = False

    last_rate_limit_at: datetime | None = None

    retry_after_seconds: float | None = None

    retry_at: datetime | None = None

    last_error: str | None = None


class ProviderLimitTracker:

    def __init__(self):

        self._states: dict[
            tuple[str, str],
            RateLimitState
        ] = {}

    def _get_or_create(
        self,
        provider: str,
        model_id: str
    ) -> RateLimitState:

        key = (provider, model_id)

        if key not in self._states:
            self._states[key] = RateLimitState(
                provider=provider,
                model_id=model_id
            )

        return self._states[key]

    def record_rate_limit(
        self,
        provider: str,
        model_id: str,
        error: RateLimitError
    ):

        state = self._get_or_create(provider, model_id)

        now = datetime.now(timezone.utc)

        state.rate_limit_observed = True
        state.last_rate_limit_at = now
        state.retry_after_seconds = error.retry_after_seconds
        state.last_error = str(error)

        if error.retry_after_seconds is not None:

            state.retry_at = now + timedelta(
                seconds=error.retry_after_seconds
            )

        else:
            state.retry_at = None

    def record_success(
        self,
        provider: str,
        model_id: str
    ):

        state = self._get_or_create(provider, model_id)

        state.rate_limit_observed = False
        state.retry_after_seconds = None
        state.retry_at = None
        state.last_error = None

    def is_cooldown_active(
        self,
        provider: str,
        model_id: str
    ) -> bool:

        state = self._get_or_create(provider, model_id)

        if state.retry_at is None:
            return False

        return datetime.now(timezone.utc) < state.retry_at

    def get_state(
        self,
        provider: str,
        model_id: str
    ) -> RateLimitState:

        return self._get_or_create(provider, model_id)

    def get_all_states(self) -> list[RateLimitState]:

        return list(self._states.values())


# Shared rate-limit tracker.
provider_limit_tracker = ProviderLimitTracker()
