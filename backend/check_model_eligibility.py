import asyncio

from app.ai.router.provider_setup import initialize_providers
from app.ai.router.model_catalog import model_catalog
from app.ai.router.model_eligibility import (
    ModelEligibilityEngine,
    ModelRequirements
)


async def main():

    initialize_providers()

    print("Refreshing model catalog...\n")

    await model_catalog.refresh_all()

    engine = ModelEligibilityEngine()

    requirements = ModelRequirements(
        required_capabilities={"content_generation"},
        minimum_context_window=16000,
        require_structured_output=False
    )

    models = model_catalog.get_all_models()

    results = [
        engine.evaluate(model, requirements)
        for model in models
    ]

    eligible = [result for result in results if result.eligible]
    ineligible = [result for result in results if not result.eligible]

    print(f"Total models: {len(results)}")
    print(f"Eligible models: {len(eligible)}")
    print(f"Ineligible models: {len(ineligible)}")

    print("\nELIGIBLE MODELS\n")

    for model in eligible:
        print(f"{model.display_name} ({model.model_id})")

    print("\nINELIGIBLE MODELS\n")

    for model in ineligible:
        print(f"{model.display_name} ({model.model_id})")
        print("Reasons:", model.reasons)


if __name__ == "__main__":
    asyncio.run(main())
