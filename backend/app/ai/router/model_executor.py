
from app.ai.router.provider_registry import provider_registry
from app.ai.router.provider_health import provider_health_tracker
from app.ai.router.usage_tracker import model_usage_tracker
from app.ai.router.provider_limits import provider_limit_tracker

from app.ai.providers.base import (
    GenerationRequest,
    GenerationResult,
    ProviderError,
    RateLimitError
)


class ModelExecutor:

    async def generate(
        self,
        provider_name: str,
        model_id: str,
        request: GenerationRequest
    ) -> GenerationResult:

        provider = provider_registry.get_provider(provider_name)

        if not provider.is_configured:
            error = ProviderError(
                f"Provider '{provider_name}' is not configured."
            )

            provider_health_tracker.record_failure(
                provider_name,
                model_id,
                error
            )

            raise error

        try:
            result = await provider.generate(
                model_id=model_id,
                request=request
            )

            # Record successful generation.
            provider_health_tracker.record_success(
                provider_name,
                model_id
            )

            # Record token usage.
            model_usage_tracker.record_usage(
                provider_name,
                model_id,
                result.usage
            )

            # Record actual quota information.
            provider_limit_tracker.record_quota_info(
                provider_name,
                model_id,
                result.rate_limits
            )

            # Clear previous cooldown after successful generation.
            provider_limit_tracker.record_success(
                provider_name,
                model_id
            )

            return result

        except Exception as exc:

            # Record rate-limit information when a 429 occurs.
            if isinstance(exc, RateLimitError):
                provider_limit_tracker.record_rate_limit(
                    provider_name,
                    model_id,
                    exc
                )

            provider_health_tracker.record_failure(
                provider_name,
                model_id,
                exc
            )

            raise


model_executor = ModelExecutor()
