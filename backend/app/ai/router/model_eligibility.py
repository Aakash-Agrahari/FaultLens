
from dataclasses import dataclass, field

from app.ai.router.model_catalog import CatalogModel


@dataclass
class ModelRequirements:
    required_capabilities: set[str] = field(
        default_factory=lambda: {"content_generation"}
    )

    minimum_context_window: int = 16000

    require_structured_output: bool = False


@dataclass
class EligibilityResult:
    provider: str
    model_id: str
    display_name: str
    eligible: bool
    reasons: list[str] = field(default_factory=list)


class ModelEligibilityEngine:

    def evaluate(
        self,
        catalog_model: CatalogModel,
        requirements: ModelRequirements
    ) -> EligibilityResult:

        model = catalog_model.model

        reasons = []

        missing_capabilities = (
            requirements.required_capabilities
            - model.capabilities
        )

        if missing_capabilities:
            reasons.append(
                f"Missing capabilities: {missing_capabilities}"
            )

        if model.context_window is None:
            reasons.append("Context window information is unavailable.")

        elif model.context_window < requirements.minimum_context_window:
            reasons.append(
                "Context window is smaller than required."
            )

        if (
            requirements.require_structured_output
            and not model.supports_structured_output
        ):
            reasons.append(
                "Structured output support is not verified."
            )

        return EligibilityResult(
            provider=catalog_model.provider,
            model_id=model.id,
            display_name=model.display_name,
            eligible=len(reasons) == 0,
            reasons=reasons
        )

    def filter_eligible_models(
        self,
        catalog_models: list[CatalogModel],
        requirements: ModelRequirements
    ) -> list[EligibilityResult]:

        return [
            self.evaluate(item, requirements)
            for item in catalog_models
            if self.evaluate(item, requirements).eligible
        ]
