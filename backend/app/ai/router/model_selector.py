from dataclasses import dataclass, field

from app.ai.router.model_catalog import CatalogModel, ModelCatalog
from app.ai.router.model_eligibility import (
    EligibilityResult,
    ModelEligibilityEngine,
    ModelRequirements,
)


@dataclass
class ModelCandidate:
    provider: str
    model_id: str
    display_name: str
    context_window: int | None
    eligibility: EligibilityResult
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
    ) -> list[ModelCandidate]:

        catalog_models = self.catalog.get_all_models()

        candidates = []

        required_tokens = None

        if estimated_input_tokens is not None:
            required_tokens = (
                estimated_input_tokens + reserved_output_tokens
            )

        for catalog_model in catalog_models:

            eligibility = self.eligibility_engine.evaluate(
                catalog_model,
                requirements,
            )

            if not eligibility.eligible:
                continue

            model = catalog_model.model
            warnings = list(eligibility.warnings)

            candidates.append(
                ModelCandidate(
                    provider=catalog_model.provider,
                    model_id=model.id,
                    display_name=model.display_name,
                    context_window=model.context_window,
                    eligibility=eligibility,
                    warnings=warnings,
                )
            )

        def ranking(candidate: ModelCandidate):

            context_window = candidate.context_window

            if required_tokens is None:
                return (
                    context_window is None,
                    -(context_window or 0),
                )

            if context_window is None:
                return (1, 0)

            if context_window >= required_tokens:
                return (0, context_window - required_tokens)

            return (
                2,
                -(context_window),
            )

        candidates.sort(key=ranking)

        return candidates
