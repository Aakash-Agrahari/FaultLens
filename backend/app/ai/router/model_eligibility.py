
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
        requirements: ModelRequirements
    ) -> EligibilityResult:

        model = catalog_model.model

        reasons = []
        warnings = []

        # Check required capabilities.
        for capability in requirements.required_capabilities:

            capability_status = model.capability_status.get(
                capability
            )

            # Backward compatibility:
            # Existing capabilities are treated as verified.
            if (
                capability_status is None
                and capability in model.capabilities
            ):
                capability_status = True

            if capability_status is True:
                continue

            elif capability_status is False:

                reasons.append(
                    f"Capability '{capability}' is verified as unsupported."
                )

            else:

                warnings.append(
                    f"Capability '{capability}' is unknown. "
                    "The model can still be attempted."
                )

        # Check context window.
        if model.context_window is None:

            warnings.append(
                "Context window is unknown. "
                "Actual input compatibility must be verified."
            )

        elif (
            model.context_window
            < requirements.minimum_context_window
        ):

            reasons.append(
                "Known context window is smaller than required."
            )

        # Check structured output.
        if requirements.require_structured_output:

            if model.supports_structured_output is False:

                reasons.append(
                    "Structured output is verified as unsupported."
                )

            elif model.supports_structured_output is None:

                warnings.append(
                    "Structured output support is unknown. "
                    "The model can still be attempted."
                )

        return EligibilityResult(
            provider=catalog_model.provider,
            model_id=model.id,
            display_name=model.display_name,
            eligible=len(reasons) == 0,
            reasons=reasons,
            warnings=warnings
        )

    def filter_eligible_models(
        self,
        catalog_models: list[CatalogModel],
        requirements: ModelRequirements
    ) -> list[EligibilityResult]:

        results = []

        for catalog_model in catalog_models:

            result = self.evaluate(
                catalog_model,
                requirements
            )

            if result.eligible:
                results.append(result)

        return results
