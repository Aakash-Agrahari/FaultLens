import asyncio

from app.ai.providers.groq_provider import GroqProvider

async def main():
    provider = GroqProvider()

    print("Provider:", provider.name)
    print("Configured:", provider.is_configured)

    print("\nDiscovering Groq models...\n")

    models = await provider.list_models()

    print(f"Discovered {len(models)} models:\n")

    for model in models:
        print("Model ID:", model.id)
        print("Display Name:", model.display_name)
        print("Context window:", model.context_window)
        print("Metadata:", model.metadata)

        print("-" * 45)


if __name__ == "__main__":
    asyncio.run(main())        