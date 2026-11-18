
from app.ai.providers.base import RateLimitError

from app.ai.router.provider_limits import (
    provider_limit_tracker
)


def main():

    provider = "groq"
    model_id = "openai/gpt-oss-20b"

    # Simulate a provider returning HTTP 429
    simulated_error = RateLimitError(
        "Too many requests",
        retry_after_seconds=30
    )

    provider_limit_tracker.record_rate_limit(
        provider,
        model_id,
        simulated_error
    )

    state = provider_limit_tracker.get_state(
        provider,
        model_id
    )

    print("Provider:", state.provider)
    print("Model:", state.model_id)

    print("Rate limit observed:", state.rate_limit_observed)

    print("Retry after:", state.retry_after_seconds, "seconds")

    print("Retry at:", state.retry_at)

    print(
        "Cooldown active:",
        provider_limit_tracker.is_cooldown_active(
            provider,
            model_id
        )
    )


if __name__ == "__main__":
    main()
