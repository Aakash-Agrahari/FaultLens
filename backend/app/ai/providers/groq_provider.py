import groq
from groq import AsyncGroq

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


class GroqProvider(BaseProvider):

    def __init__(self):
        self._api_key = settings.GROQ_API_KEY

        self._client = (
            AsyncGroq(api_key=self._api_key)
            if self._api_key
            else None
        )

    @property
    def name(self):
        return "groq"

    @property
    def is_configured(self):
        return bool(self._api_key)

    async def list_models(self) -> list[ModelInfo]:

        if not self._client:
            raise AuthenticationError(
                "Groq API key is not configured."
            )

        try:
            response = await self._client.models.list()

            models = []

            for model in response.data:

                model_id = getattr(model, "id", None)

                if not model_id:
                    continue

                models.append(
                    ModelInfo(
                        id=model_id,
                        display_name=model_id,
                        capabilities=set(),
                        context_window=getattr(
                            model,
                            "context_window",
                            None
                        ),
                        supports_structured_output=False,
                        metadata={
                            "provider": "groq",
                            "owned_by": getattr(
                                model,
                                "owned_by",
                                None
                            ),
                            "active": getattr(
                                model,
                                "active",
                                None
                            ),
                            "object": getattr(
                                model,
                                "object",
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
                "Groq API key is not configured."
            )

        try:
            messages = [
                {
                    "role": "system",
                    "content": request.system_prompt
                },
                {
                    "role": "user",
                    "content": request.user_prompt
                }
            ]

            generation_args = {
                "model": model_id,
                "messages": messages,
                "temperature": request.temperature
            }

            if request.max_output_tokens is not None:
                generation_args["max_completion_tokens"] = (
                    request.max_output_tokens
                )

            if request.response_schema:
                generation_args["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "faultlens_response",
                        "strict": True,
                        "schema": request.response_schema
                    }
                }

            response = await (
                self._client.chat.completions.create(
                    **generation_args
                )
            )

            if not response.choices:
                raise ProviderError(
                    "Groq returned no response choices."
                )

            choice = response.choices[0]

            content = choice.message.content

            if not content:
                raise ProviderError(
                    "Groq returned an empty response."
                )

            usage = {}

            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }

            return GenerationResult(
                content=content,
                provider=self.name,
                model=model_id,
                usage=usage,
                finish_reason=choice.finish_reason
            )

        except ProviderError:
            raise

        except Exception as exc:
            self._raise_provider_error(exc)

    
    @staticmethod
    def _raise_provider_error(exc):

        status_code = getattr(exc, "status_code", None)

        if status_code == 429:

            response = getattr(exc, "response", None)

            headers = (
                response.headers
                if response is not None
                else {}
            )

            retry_after = headers.get("retry-after")

            retry_after_seconds = None

            if retry_after is not None:
                try:
                    retry_after_seconds = float(retry_after)
                except (ValueError, TypeError):
                    pass

            raise RateLimitError(
                str(exc),
                retry_after_seconds=retry_after_seconds
            ) from exc

        if status_code in (401, 403):
            raise AuthenticationError(str(exc)) from exc

        if status_code == 404:
            raise ModelUnavailableError(str(exc)) from exc

        if (
            isinstance(status_code, int)
            and status_code >= 500
        ):
            raise TemporaryProviderError(str(exc)) from exc

        if isinstance(
            exc,
            (
                groq.APIConnectionError,
                groq.APITimeoutError
            )
        ):
            raise TemporaryProviderError(str(exc)) from exc

        raise ProviderError(str(exc)) from exc


    @staticmethod
    def _extract_rate_limits(headers):
        header_names = [
            "x-ratelimit-limit-requests",
            "x-ratelimit-remaining-requests",
            "x-ratelimit-reset-requests",
            "x-ratelimit-limit-tokens",
            "x-ratelimit-remaining-tokens",
            "x-ratelimit-reset-tokens",
        ]

        return {
            name: headers[name]
            for name in header_names
            if name in headers
        }