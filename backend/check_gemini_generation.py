
import asyncio

from app.ai.router.provider_setup import initialize_providers
from app.ai.providers.base import GenerationRequest


async def main():
    registry = initialize_providers()

    gemini = registry.get_provider("gemini")

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

    print("Sending request to Gemini...\n")

    result = await gemini.generate(
        model_id="gemini-3.5-flash-lite",
        request=request
    )

    print("Provider:", result.provider)
    print("Model:", result.model)
    print("\nGenerated response:\n")
    print(result.content)


if __name__ == "__main__":
    asyncio.run(main())
