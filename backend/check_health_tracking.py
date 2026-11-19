import asyncio

from app.ai.router.provider_setup import initialize_providers

from app.ai.router.model_executor import model_executor

from app.ai.router.provider_health import provider_health_tracker

from app.ai.providers.base import GenerationRequest

from app.ai.router.usage_tracker import model_usage_tracker

from app.ai.router.provider_limits import provider_limit_tracker

async def main():

    initialize_providers()

    request = GenerationRequest(
        system_prompt="You are a helpful software engineering assistant.",
        user_prompt="Explain a database connection timeout in two sentences.",
        temperature=0.2,
        max_output_tokens=150
    )

    models_to_test = [
        ("gemini", "gemini-3.5-flash-lite"),
        ("groq", "openai/gpt-oss-20b")
    ]

    for provider_name, model_id in models_to_test:

        print(f"\nTesting {provider_name}: {model_id}")

        try:

            result = await model_executor.generate(
                provider_name=provider_name,
                model_id=model_id,
                request=request
            )

            print("Generation successful!")
            print("Provider:", result.provider)
            print("Model:", result.model)
            print("Response:", result.content)

        except Exception as exc:

            print("Generation failed:", str(exc))

    print("\n========== MODEL HEALTH ==========\n")

    for health in provider_health_tracker.get_all_health():

        print("Provider:", health.provider)
        print("Model:", health.model_id)
        print("Status:", health.status)
        print("Consecutive failures:", health.consecutive_failures)
        print("Last error:", health.last_error)
        print("-" * 45)

    print("\n========== MODEL USAGE ==========\n")

    for usage in model_usage_tracker.get_all_usage():

        print("Provider:", usage.provider)
        print("Model:", usage.model_id)

        print("Successful requests:", usage.successful_requests)

        print("Prompt tokens:", usage.prompt_tokens)
        print("Completion tokens:", usage.completion_tokens)
        print("Total tokens:", usage.total_tokens)

        print("Last used:", usage.last_used_at)

        print("-" * 45)

    print("\n========== PROVIDER QUOTA INFORMATION ==========\n")

    for state in provider_limit_tracker.get_all_states():

        print("Provider:", state.provider)
        print("Model:", state.model_id)

        print("\nRequest Quota:")
        print("Request limit:", state.request_limit)
        print("Remaining requests:", state.remaining_requests)
        print("Request reset:", state.request_reset)

        print("\nToken Quota:")
        print("Token limit:", state.token_limit)
        print("Remaining tokens:", state.remaining_tokens)
        print("Token reset:", state.token_reset)

        print("\nRate Limit Status:")
        print("Rate limit observed:", state.rate_limit_observed)
        print("Cooldown active:", provider_limit_tracker.is_cooldown_active(
            state.provider,
            state.model_id
        ))

        print("Last quota update:", state.last_quota_update)
        print("-" * 50)    

if __name__ == "__main__":
    asyncio.run(main())
