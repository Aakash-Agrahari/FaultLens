import asyncio
from types import SimpleNamespace

from app.ai.providers.base import GenerationRequest, GenerationResult
from app.ai.router.fallback_executor import FallbackExecutor


class FakeSelector:

    def select_candidates(self, **kwargs):

        return [
            SimpleNamespace(
                provider="test_provider",
                model_id="model_1",
            ),
            SimpleNamespace(
                provider="test_provider",
                model_id="model_2",
            ),
            SimpleNamespace(
                provider="test_provider",
                model_id="model_3",
            ),
        ]


class FakeExecutor:

    def __init__(self):
        self.calls = []

    async def generate(self, provider_name, model_id, request):

        self.calls.append(model_id)

        if model_id == "model_1":
            raise RuntimeError("Simulated rate limit")

        if model_id == "model_2":
            raise RuntimeError("Simulated temporary failure")

        return GenerationResult(
            content="Fallback successful!",
            provider=provider_name,
            model=model_id,
            usage={
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
        )


async def main():

    selector = FakeSelector()

    fallback = FallbackExecutor(selector)

    fake_executor = FakeExecutor()

    # Replace the real executor with our local simulator.
    fallback.executor = fake_executor

    request = GenerationRequest(
        system_prompt="You are a helpful assistant.",
        user_prompt="Explain a database connection timeout.",
        max_output_tokens=200,
    )

    result = await fallback.generate(
        request=request,
        estimated_input_tokens=100,
    )

    print("\nFALLBACK TEST RESULT\n")

    print("Models attempted:", fake_executor.calls)

    print("Successful provider:", result.provider)

    print("Successful model:", result.model)

    print("Response:", result.content)

    print("Token usage:", result.usage)

    if (
        fake_executor.calls == ["model_1", "model_2", "model_3"]
        and result.model == "model_3"
        and result.content == "Fallback successful!"
    ):
        print("\nPASSED: Automatic fallback works correctly.")
    else:
        print("\nFAILED: Unexpected fallback behavior.")


if __name__ == "__main__":
    asyncio.run(main())
