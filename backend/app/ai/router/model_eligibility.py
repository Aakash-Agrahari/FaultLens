
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
    warnings: list[str] = field(default_factory=list)


class ModelEligibilityEngine:

    def evaluate(
        self,
        catalog_model: CatalogModel,
        requirements: ModelRequirements,
    ) -> EligibilityResult:

        model = catalog_model.model

        reasons = []
        warnings = []

        # Check required capabilities.
        for capability in requirements.required_capabilities:

            capability_status = model.capability_status.get(capability)

            if capability_status is False:
                reasons.append(
                    f"Model is explicitly marked as not supporting {capability}."
                )

            elif capability_status is None and capability not in model.capabilities:
                warnings.append(
                    f"Support for {capability} has not been verified."
                )

        # Context window is a preference for model selection,
        # not a permanent eligibility restriction.
        if model.context_window is None:
            warnings.append(
                "Context window information is unavailable."
            )

        elif model.context_window < requirements.minimum_context_window:
            warnings.append(
                f"Context window is below the preferred "
                f"{requirements.minimum_context_window} tokens."
            )

        # Check structured-output support only when required.
        if requirements.require_structured_output:

            if model.supports_structured_output is False:
                reasons.append(
                    "Model is explicitly marked as not supporting structured output."
                )

            elif model.supports_structured_output is None:
                warnings.append(
                    "Structured-output support has not been verified."
                )

        return EligibilityResult(
            provider=catalog_model.provider,
            model_id=model.id,
            display_name=model.display_name,
            eligible=len(reasons) == 0,
            reasons=reasons,
            warnings=warnings,
        )

    def filter_eligible_models(
        self,
        catalog_models: list[CatalogModel],
        requirements: ModelRequirements,
    ) -> list[EligibilityResult]:

        results = []

        for catalog_model in catalog_models:
            result = self.evaluate(catalog_model, requirements)

            if result.eligible:
                results.append(result)

        return results
