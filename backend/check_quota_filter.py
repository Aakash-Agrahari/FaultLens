import asyncio

from app.ai.router.provider_setup import initialize_providers
from app.ai.router.model_catalog import ModelCatalog
from app.ai.router.model_eligibility import ModelRequirements
from app.ai.router.model_selector import ModelSelector
from app.ai.router.provider_limits import provider_limit_tracker


async def main():

    registry = initialize_providers()
    catalog = ModelCatalog(registry)

    await catalog.refresh_all()

    all_models = catalog.get_all_models()

    if not all_models:
        print("No models discovered.")
        return

    test_model = all_models[0]

    provider_limit_tracker.record_quota_info(
        test_model.provider,
        test_model.model.id,
        {
            "x-ratelimit-remaining-tokens": "0",
            "x-ratelimit-remaining-requests": "10",
        },
    )

    selector = ModelSelector(catalog)

    candidates = selector.select_candidates(
        requirements=ModelRequirements(),
        estimated_input_tokens=1000,
        reserved_output_tokens=500,
    )

    selected_ids = {
        (candidate.provider, candidate.model_id)
        for candidate in candidates
    }

    test_key = (test_model.provider, test_model.model.id)

    if test_key in selected_ids:
        print("FAILED: Exhausted model was still selected.")
    else:
        print("PASSED: Model with zero remaining tokens was skipped.")

    print(f"Total candidates remaining: {len(candidates)}")


if __name__ == "__main__":
    asyncio.run(main())
