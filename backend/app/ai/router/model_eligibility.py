from dataclasses import dataclass, field

from app.ai.router.model_catalog import CatalogModel


@dataclass
class ModelRequirements:
    # Capabilities required for a particular task.
    required_capabilities: set[str] = field(
        default_factory=lambda: {"content_generation"}
    )

    # Minimum context window required.
    minimum_context_window: int = 16000

    # Whether structured output is mandatory.
    require_structured_output: bool = False

    # Whether models with unverified capabilities can be considered.
    allow_unknown_capabilities: bool = False


@dataclass
class EligibilityResult:
    provider: str
    model_id: str
    display_name: str
    eligible: bool

    reasons: list[str] = field(default_factory=list)

    # Capabilities for which verification is unavailable.
    unverified_capabilities: list[str] = field(
        default_factory=list
    )


class ModelEligibilityEngine:

    def evaluate(
        self,
        catalog_model: CatalogModel,
        requirements: ModelRequirements
    ) -> EligibilityResult:

        model = catalog_model.model

        reasons = []
        unverified_capabilities = []

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
                    f"Capability '{capability}' is not supported."
                )

            else:
                unverified_capabilities.append(capability)

                if not requirements.allow_unknown_capabilities:
                    reasons.append(
                        f"Capability '{capability}' is not verified."
                    )

        # Check context window.
        if model.context_window is None:

            reasons.append(
                "Context window information is unavailable."
            )

        elif (
            model.context_window
            < requirements.minimum_context_window
        ):

            reasons.append(
                "Context window is smaller than required."
            )

        # Check structured output support.
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
            reasons=reasons,
            unverified_capabilities=unverified_capabilities
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
