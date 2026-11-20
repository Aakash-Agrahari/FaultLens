import asyncio

from app.ai.router.provider_setup import initialize_providers
from app.ai.router.model_catalog import ModelCatalog
from app.ai.router.model_eligibility import ModelRequirements
from app.ai.router.model_selector import ModelSelector


async def main():

    print("Initializing providers...")

    registry = initialize_providers()

    catalog = ModelCatalog(registry)

    print("Refreshing model catalog...")

    refresh_result = await catalog.refresh_all()

    print(f"Catalog refresh result: {refresh_result}")

    selector = ModelSelector(catalog)

    requirements = ModelRequirements(
        required_capabilities={"content_generation"},
        minimum_context_window=16000,
    )

    candidates = selector.select_candidates(
        requirements=requirements,
        estimated_input_tokens=6000,
        reserved_output_tokens=2000,
    )

    print(f"\nTotal selected candidates: {len(candidates)}")
    print("\nRANKED MODEL CANDIDATES\n")

    for index, candidate in enumerate(candidates, start=1):

        print(
            f"{index}. {candidate.display_name} "
            f"({candidate.provider}/{candidate.model_id})"
        )

        print(
            f"   Context window: "
            f"{candidate.context_window or 'Unknown'}"
        )

        if candidate.warnings:
            print(f"   Warnings: {candidate.warnings}")

        print()


if __name__ == "__main__":
    asyncio.run(main())
