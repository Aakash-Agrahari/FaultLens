import asyncio

from app.ai.router.provider_setup import initialize_providers


async def main():
    registry = initialize_providers()

    print("Registered providers:")
    print(registry.get_registered_provider_names())

    print("\nDiscovering Gemini models...")

    models = await registry.discover_models("gemini")

    print(f"\nDiscovered {len(models)} models:\n")

    for model in models:
        print(f"Model ID: {model.id}")
        print(f"Display name: {model.display_name}")
        print(f"Capabilities: {model.capabilities}")
        print(f"Context window: {model.context_window}")
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(main())
