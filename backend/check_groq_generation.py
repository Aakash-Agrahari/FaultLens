import asyncio

from app.ai.router.provider_setup import initialize_providers
from app.ai.providers.base import GenerationRequest


async def main():

    registry = initialize_providers()

    groq_provider = registry.get_provider("groq")

    request = GenerationRequest(
        system_prompt=(
            "You are an AI assistant helping software engineers "
            "investigate application incidents."
        ),
        user_prompt=(
            "Explain what a database connection timeout is, "
            "give two common causes, and suggest one debugging step."
        ),
        temperature=0.2,
        max_output_tokens=300
    )

    model_id = "openai/gpt-oss-20b"

    print("Sending request to Groq...\n")

    result = await groq_provider.generate(
        model_id=model_id,
        request=request
    )

    print("Provider:", result.provider)
    print("Model:", result.model)
    print("Usage:", result.usage)
    print("Finish reason:", result.finish_reason)

    print("\nGenerated response:\n")
    print(result.content)


if __name__ == "__main__":
    asyncio.run(main())
