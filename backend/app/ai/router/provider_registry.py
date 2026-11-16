
from app.ai.providers.base import (
    BaseProvider,
    ModelInfo,
    ProviderError
)


class ProviderNotRegisteredError(ProviderError):
    """Raised when a provider is not registered."""


class ProviderNotConfiguredError(ProviderError):
    """Raised when a provider has no valid credentials."""


class ProviderRegistry:

    def __init__(self):
        self._providers: dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider):
        provider_name = provider.name.lower().strip()

        if not provider_name:
            raise ValueError("Provider name cannot be empty.")

        if provider_name in self._providers:
            raise ValueError(
                f"Provider '{provider_name}' is already registered."
            )

        self._providers[provider_name] = provider

    def get_provider(self, provider_name: str) -> BaseProvider:
        provider_name = provider_name.lower().strip()

        provider = self._providers.get(provider_name)

        if provider is None:
            raise ProviderNotRegisteredError(
                f"Provider '{provider_name}' is not registered."
            )

        return provider

    def get_configured_providers(self) -> list[BaseProvider]:
        return [
            provider
            for provider in self._providers.values()
            if provider.is_configured
        ]

    def get_registered_provider_names(self) -> list[str]:
        return list(self._providers.keys())

    async def discover_models(self, provider_name: str) -> list[ModelInfo]:
        provider = self.get_provider(provider_name)

        if not provider.is_configured:
            raise ProviderNotConfiguredError(
                f"Provider '{provider_name}' is not configured."
            )

        return await provider.list_models()


# Shared registry instance used across the application
provider_registry = ProviderRegistry()
