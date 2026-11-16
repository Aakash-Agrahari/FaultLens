
from google import genai

from app.core.config import settings

from app.ai.providers.base import (
    BaseProvider,
    ModelInfo,
    GenerationRequest,
    GenerationResult,
    ProviderError,
    RateLimitError,
    AuthenticationError,
    ModelUnavailableError,
    TemporaryProviderError
)


class GeminiProvider(BaseProvider):

    def __init__(self):
        self._api_key = settings.GEMINI_API_KEY

        self._client = (
            genai.Client(api_key=self._api_key)
            if self._api_key
            else None
        )

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    async def list_models(self) -> list[ModelInfo]:

        if not self._client:
            raise AuthenticationError(
                "Gemini API key is not configured"
            )

        try:
            models = []

            pager = await self._client.aio.models.list()

            async for model in pager:

                supported_actions = (
                    getattr(model, "supported_actions", None) or []
                )

                if "generateContent" not in supported_actions:
                    continue

                model_id = getattr(model, "name", "")

                if not model_id:
                    continue

                model_id = model_id.split("/", 1)[-1]

                capabilities = {"text_generation"}

                models.append(
                    ModelInfo(
                        id=model_id,
                        display_name=(
                            getattr(model, "display_name", None)
                            or model_id
                        ),
                        capabilities=capabilities,
                        context_window=getattr(
                            model,
                            "input_token_limit",
                            None
                        ),
                        supports_structured_output=False,
                        metadata={
                            "provider": "gemini",
                            "supported_actions": list(
                                supported_actions
                            ),
                            "output_token_limit": getattr(
                                model,
                                "output_token_limit",
                                None
                            )
                        }
                    )
                )

            return models

        except Exception as exc:
            self._raise_provider_error(exc)

    async def generate(
        self,
        model_id: str,
        request: GenerationRequest
    ) -> GenerationResult:

        if not self._client:
            raise AuthenticationError(
                "Gemini API key is not configured"
            )

        try:
            generation_config = {
                "temperature": request.temperature
            }

            if request.max_output_tokens is not None:
                generation_config["max_output_tokens"] = (
                    request.max_output_tokens
                )

            interaction_args = {
                "model": model_id,
                "system_instruction": request.system_prompt,
                "input": request.user_prompt,
                "generation_config": generation_config
            }

            if request.response_schema:
                interaction_args["response_format"] = {
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": request.response_schema
                }

            response = await self._client.aio.interactions.create(
                **interaction_args
            )

            content = response.output_text

            if not content:
                raise ProviderError(
                    "Gemini returned an empty response"
                )

            return GenerationResult(
                content=content,
                provider=self.name,
                model=model_id,
                usage={},
                finish_reason=None
            )

        except ProviderError:
            raise

        except Exception as exc:
            self._raise_provider_error(exc)

    @staticmethod
    def _raise_provider_error(exc: Exception):
        status_code = (
            getattr(exc, "status_code", None)
            or getattr(exc, "code", None)
        )

        if status_code == 429:
            raise RateLimitError(
                "Gemini rate limit or quota reached"
            ) from exc

        if status_code in (401, 403):
            raise AuthenticationError(
                "Gemini authentication failed or access was denied"
            ) from exc

        if status_code == 404:
            raise ModelUnavailableError(
                "Requested Gemini model was not found"
            ) from exc

        if isinstance(status_code, int) and status_code >= 500:
            raise TemporaryProviderError(
                "Gemini service is temporarily unavailable"
            ) from exc

        raise ProviderError(
            f"Gemini provider request failed: {exc}"
        ) from exc
