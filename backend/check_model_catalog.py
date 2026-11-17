import asyncio

from app.ai.router.provider_setup import initialize_providers
from app.ai.router.model_catalog import model_catalog


async def main():

    initialize_providers()

    print("Refreshing model catalog...\n")

    result = await model_catalog.refresh_all()

    models = result["models"]

    print(f"Total discovered models: {len(models)}\n")

    for item in models:
        print(f"Provider: {item.provider}")
        print(f"Model: {item.model.display_name}")
        print(f"Model ID: {item.model.id}")
        print(f"Capabilities: {item.model.capabilities}")
        print("-" * 45)

    if result["failures"]:
        print("\nProvider failures:")

        for provider, error in result["failures"].items():
            print(f"{provider}: {error}")


if __name__ == "__main__":
    asyncio.run(main())
