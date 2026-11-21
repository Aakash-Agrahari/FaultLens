from dataclasses import dataclass, field

from app.ai.router.model_catalog import ModelCatalog
from app.ai.router.model_eligibility import (
    EligibilityResult,
    ModelEligibilityEngine,
    ModelRequirements,
)
from app.ai.router.provider_health import provider_health_tracker
from app.ai.router.provider_limits import provider_limit_tracker


@dataclass
class ModelCandidate:
    provider: str
    model_id: str
    display_name: str
    context_window: int | None
    eligibility: EligibilityResult

    health_status: str
    consecutive_failures: int

    cooldown_active: bool

    remaining_requests: int | None
    remaining_tokens: int | None

    warnings: list[str] = field(default_factory=list)


class ModelSelector:

    def __init__(
        self,
        catalog: ModelCatalog,
        eligibility_engine: ModelEligibilityEngine | None = None,
    ):
        self.catalog = catalog

        self.eligibility_engine = (
            eligibility_engine or ModelEligibilityEngine()
        )

    def select_candidates(
        self,
        requirements: ModelRequirements,
        estimated_input_tokens: int | None = None,
        reserved_output_tokens: int = 0,
        attempted_models: set[tuple[str, str]] | None = None,
    ) -> list[ModelCandidate]:

        catalog_models = self.catalog.get_all_models()

        candidates = []

        attempted_models = attempted_models or set()

        required_tokens = None

        if estimated_input_tokens is not None:
            required_tokens = (
                estimated_input_tokens + reserved_output_tokens
            )

        for catalog_model in catalog_models:

            provider = catalog_model.provider
            model = catalog_model.model

            # Avoid repeating a model during the same routing attempt.
            if (provider, model.id) in attempted_models:
                continue

            eligibility = self.eligibility_engine.evaluate(
                catalog_model,
                requirements,
            )

            if not eligibility.eligible:
                continue

            health = provider_health_tracker.get_health(
                provider,
                model.id,
            )

            limit_state = provider_limit_tracker.get_state(
                provider,
                model.id,
            )

            cooldown_active = (
                provider_limit_tracker.is_cooldown_active(
                    provider,
                    model.id,
                )
            )

            # Skip models currently in cooldown.
            if cooldown_active:
                continue

            # Skip models whose latest reported quota is exhausted.
            if (
                limit_state.remaining_tokens == 0
                or limit_state.remaining_requests == 0
            ):
                continue

            warnings = list(eligibility.warnings)

            if health.status != "healthy":
                warnings.append(
                    f"Model health status: {health.status}"
                )

            if model.context_window is not None:
                if (
                    required_tokens is not None
                    and model.context_window < required_tokens
                ):
                    warnings.append(
                        "Context window is smaller than this request."
                    )

            if limit_state.remaining_tokens == 0:
                warnings.append(
                    "No remaining tokens reported in the latest quota data."
                )

            if limit_state.remaining_requests == 0:
                warnings.append(
                    "No remaining requests reported in the latest quota data."
                )

            candidates.append(
                ModelCandidate(
                    provider=provider,
                    model_id=model.id,
                    display_name=model.display_name,
                    context_window=model.context_window,
                    eligibility=eligibility,
                    health_status=health.status,
                    consecutive_failures=health.consecutive_failures,
                    cooldown_active=cooldown_active,
                    remaining_requests=limit_state.remaining_requests,
                    remaining_tokens=limit_state.remaining_tokens,
                    warnings=warnings,
                )
            )

        def ranking(candidate: ModelCandidate):

            model = next(
                item.model
                for item in catalog_models
                if (
                    item.provider == candidate.provider
                    and item.model.id == candidate.model_id
                )
            )

            # Prefer models with verified task capabilities.
            capability_rank = 0

            for capability in requirements.required_capabilities:

                status = model.capability_status.get(capability)

                if status is None and capability not in model.capabilities:
                    capability_rank = 1
                    break

            # Prefer models that can fit the complete request.
            if required_tokens is None:
                context_rank = 0

            elif model.context_window is None:
                context_rank = 1

            elif model.context_window >= required_tokens:
                context_rank = 0

            else:
                context_rank = 2

            # Prefer models with successful execution history.
            health_ranks = {
                "healthy": 0,
                "unknown": 1,
                "temporarily_unavailable": 2,
                "rate_limited": 3,
                "provider_error": 3,
                "unknown_error": 3,
                "authentication_error": 4,
                "model_unavailable": 4,
            }

            health_rank = health_ranks.get(
                candidate.health_status,
                3,
            )

            # Prefer models with known positive quota availability.
            if (
                candidate.remaining_tokens is not None
                and candidate.remaining_tokens > 0
            ):
                quota_rank = 0
                quota_amount = candidate.remaining_tokens

            elif (
                candidate.remaining_tokens is None
                and candidate.remaining_requests != 0
            ):
                quota_rank = 1
                quota_amount = float("inf")

            else:
                quota_rank = 2
                quota_amount = float("inf")

            return (
                capability_rank,
                context_rank,
                health_rank,
                quota_rank,
                quota_amount,
            )

        candidates.sort(key=ranking)

        return candidates
