
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from app.ai.providers.base import RateLimitError


@dataclass
class RateLimitState:
    provider: str
    model_id: str

    # Rate-limit status
    rate_limit_observed: bool = False
    last_rate_limit_at: datetime | None = None
    retry_after_seconds: float | None = None
    retry_at: datetime | None = None
    last_error: str | None = None

    # Request quota information
    request_limit: int | None = None
    remaining_requests: int | None = None
    request_reset: str | None = None

    # Token quota information
    token_limit: int | None = None
    remaining_tokens: int | None = None
    token_reset: str | None = None

    # Tracking timestamp
    last_quota_update: datetime | None = None


class ProviderLimitTracker:

    def __init__(self):
        self._states: dict[
            tuple[str, str],
            RateLimitState
        ] = {}

    def _get_or_create(self, provider, model_id):

        key = (provider, model_id)

        if key not in self._states:
            self._states[key] = RateLimitState(
                provider=provider,
                model_id=model_id
            )

        return self._states[key]

    @staticmethod
    def _to_int(value):

        if value is None:
            return None

        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def record_quota_info(self, provider, model_id, rate_limits):

        if not rate_limits:
            return

        state = self._get_or_create(provider, model_id)

        # Update request quota information.
        if "x-ratelimit-limit-requests" in rate_limits:
            state.request_limit = self._to_int(
                rate_limits["x-ratelimit-limit-requests"]
            )

        if "x-ratelimit-remaining-requests" in rate_limits:
            state.remaining_requests = self._to_int(
                rate_limits["x-ratelimit-remaining-requests"]
            )

        if "x-ratelimit-reset-requests" in rate_limits:
            state.request_reset = rate_limits[
                "x-ratelimit-reset-requests"
            ]

        # Update token quota information.
        if "x-ratelimit-limit-tokens" in rate_limits:
            state.token_limit = self._to_int(
                rate_limits["x-ratelimit-limit-tokens"]
            )

        if "x-ratelimit-remaining-tokens" in rate_limits:
            state.remaining_tokens = self._to_int(
                rate_limits["x-ratelimit-remaining-tokens"]
            )

        if "x-ratelimit-reset-tokens" in rate_limits:
            state.token_reset = rate_limits[
                "x-ratelimit-reset-tokens"
            ]

        state.last_quota_update = datetime.now(timezone.utc)

    def record_rate_limit(self, provider, model_id, error):

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

        # Capture quota information from the failed response too.
        self.record_quota_info(
            provider,
            model_id,
            error.rate_limit_headers
        )

    def record_success(self, provider, model_id):

        state = self._get_or_create(provider, model_id)

        state.rate_limit_observed = False
        state.retry_after_seconds = None
        state.retry_at = None
        state.last_error = None

    def is_cooldown_active(self, provider, model_id):

        state = self._get_or_create(provider, model_id)

        if state.retry_at is None:
            return False

        return datetime.now(timezone.utc) < state.retry_at

    def get_state(self, provider, model_id):

        return self._get_or_create(provider, model_id)

    def get_all_states(self):

        return list(self._states.values())


provider_limit_tracker = ProviderLimitTracker()
