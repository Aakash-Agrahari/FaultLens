
from dataclasses import dataclass
from typing import Callable

from app.ai.providers.base import (
    AuthenticationError,
    GenerationRequest,
    GenerationResult,
)

from app.ai.router.model_selector import ModelSelector
from app.ai.router.model_eligibility import ModelRequirements
from app.ai.router.model_executor import model_executor


@dataclass
class FallbackAttempt:
    provider: str
    model_id: str
    success: bool
    error: str | None = None


class FallbackExecutionError(Exception):

    def __init__(self, attempts: list[FallbackAttempt]):
        self.attempts = attempts

        message = (
            "All available model candidates failed. "
            f"Total attempts: {len(attempts)}."
        )

        super().__init__(message)


class FallbackExecutor:

    def __init__(self, selector: ModelSelector):
        self.selector = selector
        self.executor = model_executor

    async def generate(
        self,
        request: GenerationRequest,
        requirements: ModelRequirements | None = None,
        estimated_input_tokens: int | None = None,
        max_attempts: int | None = None,
        result_validator: Callable[[GenerationResult], None] | None = None,
    ) -> GenerationResult:

        if requirements is None:
            requirements = ModelRequirements()

        reserved_output_tokens = request.max_output_tokens or 0

        candidates = self.selector.select_candidates(
            requirements=requirements,
            estimated_input_tokens=estimated_input_tokens,
            reserved_output_tokens=reserved_output_tokens,
        )

        if not candidates:
            raise FallbackExecutionError([])

        attempts = []
        unavailable_providers = set()

        attempt_limit = (
            len(candidates)
            if max_attempts is None
            else max(0, min(max_attempts, len(candidates)))
        )

        for candidate in candidates:

            if len(attempts) >= attempt_limit:
                break

            provider = candidate.provider
            model_id = candidate.model_id

            if provider in unavailable_providers:
                continue

            try:

                result = await self.executor.generate(
                    provider_name=provider,
                    model_id=model_id,
                    request=request,
                )

                # Validate the generated content before accepting it.
                if result_validator is not None:
                    result_validator(result)

                attempts.append(
                    FallbackAttempt(
                        provider=provider,
                        model_id=model_id,
                        success=True,
                    )
                )

                return result

            except AuthenticationError as exc:

                unavailable_providers.add(provider)

                attempts.append(
                    FallbackAttempt(
                        provider=provider,
                        model_id=model_id,
                        success=False,
                        error=str(exc),
                    )
                )

            except Exception as exc:

                attempts.append(
                    FallbackAttempt(
                        provider=provider,
                        model_id=model_id,
                        success=False,
                        error=str(exc),
                    )
                )

        raise FallbackExecutionError(attempts)
