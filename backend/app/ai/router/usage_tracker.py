from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ModelUsage:

    provider: str
    model_id: str

    successful_requests: int = 0

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    last_used_at: datetime | None = None


class ModelUsageTracker:

    def __init__(self):

        self._usage: dict[tuple[str, str], ModelUsage] = {}

    def _get_or_create(
        self,
        provider: str,
        model_id: str
    ) -> ModelUsage:

        key = (provider, model_id)

        if key not in self._usage:
            self._usage[key] = ModelUsage(
                provider=provider,
                model_id=model_id
            )

        return self._usage[key]

    def record_usage(
        self,
        provider: str,
        model_id: str,
        usage: dict[str, int] | None
    ):

        stats = self._get_or_create(provider, model_id)

        stats.successful_requests += 1
        stats.last_used_at = datetime.now(timezone.utc)

        usage = usage or {}

        stats.prompt_tokens += usage.get("prompt_tokens", 0)
        stats.completion_tokens += usage.get("completion_tokens", 0)
        stats.total_tokens += usage.get("total_tokens", 0)

    def get_usage(
        self,
        provider: str,
        model_id: str
    ) -> ModelUsage:

        return self._get_or_create(provider, model_id)

    def get_all_usage(self) -> list[ModelUsage]:

        return list(self._usage.values())


# Shared usage tracker.
model_usage_tracker = ModelUsageTracker()
