
import asyncio
from types import SimpleNamespace

from app.ai.providers.base import GenerationRequest
from app.ai.router.fallback_executor import (
    FallbackExecutor,
    FallbackExecutionError,
)


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

        raise RuntimeError(
            f"Simulated failure for {model_id}"
        )


async def main():

    fallback = FallbackExecutor(FakeSelector())

    fake_executor = FakeExecutor()
    fallback.executor = fake_executor

    request = GenerationRequest(
        system_prompt="You are a helpful assistant.",
        user_prompt="Investigate a database connection failure.",
        max_output_tokens=200,
    )

    try:

        await fallback.generate(
            request=request,
            estimated_input_tokens=100,
        )

        print("FAILED: Expected fallback execution to fail.")

    except FallbackExecutionError as exc:

        print("\nALL-MODELS-FAIL TEST RESULT\n")

        print("Models attempted:", fake_executor.calls)
        print("Total recorded attempts:", len(exc.attempts))

        for attempt in exc.attempts:
            print(
                f"{attempt.provider}/{attempt.model_id}: "
                f"success={attempt.success}, "
                f"error={attempt.error}"
            )

        if (
            len(fake_executor.calls) == 3
            and len(exc.attempts) == 3
            and all(not attempt.success for attempt in exc.attempts)
        ):
            print(
                "\nPASSED: All failures were handled correctly."
            )
        else:
            print("\nFAILED: Unexpected fallback behavior.")


if __name__ == "__main__":
    asyncio.run(main())
