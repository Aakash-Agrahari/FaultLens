
from app.ai.router.provider_registry import provider_registry

from app.ai.router.provider_health import (
    provider_health_tracker
)

from app.ai.router.usage_tracker import (
    model_usage_tracker
)

from app.ai.providers.base import (
    GenerationRequest,
    GenerationResult,
    ProviderError
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

            # Record successful model health.
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

            return result

        except Exception as exc:

            provider_health_tracker.record_failure(
                provider_name,
                model_id,
                exc
            )

            raise


# Shared executor.
model_executor = ModelExecutor()
