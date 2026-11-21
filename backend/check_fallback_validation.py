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
        ]


class FakeExecutor:

    def __init__(self):
        self.calls = []

    async def generate(self, provider_name, model_id, request):

        self.calls.append(model_id)

        content = (
            "INVALID JSON"
            if model_id == "model_1"
            else '{"status": "valid"}'
        )

        return GenerationResult(
            content=content,
            provider=provider_name,
            model=model_id,
        )


def validate_result(result):

    if not result.content.startswith("{"):
        raise ValueError("Generated response is not valid JSON.")


async def main():

    fallback = FallbackExecutor(FakeSelector())

    fake_executor = FakeExecutor()
    fallback.executor = fake_executor

    request = GenerationRequest(
        system_prompt="Return JSON.",
        user_prompt="Test fallback validation.",
        max_output_tokens=200,
    )

    result = await fallback.generate(
        request=request,
        result_validator=validate_result,
    )

    print("Models attempted:", fake_executor.calls)
    print("Successful model:", result.model)
    print("Response:", result.content)

    if (
        fake_executor.calls == ["model_1", "model_2"]
        and result.model == "model_2"
    ):
        print("\nPASSED: Invalid output triggered automatic fallback.")
    else:
        print("\nFAILED: Unexpected validation behavior.")


if __name__ == "__main__":
    asyncio.run(main())
