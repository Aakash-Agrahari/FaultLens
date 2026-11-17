from dataclasses import dataclass

from app.ai.providers.base import ModelInfo, ProviderError
from app.ai.router.provider_registry import ProviderRegistry
from app.ai.router.provider_registry import provider_registry

@dataclass
class CatalogModel:
    provider: str
    model: ModelInfo


class ModelCatalog:

    def __init__(self, registry: ProviderRegistry):
        self.registry = registry

        self._models: dict[tuple[str, str], CatalogModel] = {}
        self._provider_errors: dict[str, str] = {}

    async def refresh_provider(self, provider_name: str):
        provider = self.registry.get_provider(provider_name)

        if not provider.is_configured:
            raise ProviderError(
                f"Provider '{provider_name}' is not configured."
            )

        discovered_models = await provider.list_models()

        # Replace this provider's previous catalog entries.
        self._models = {
            key: value
            for key, value in self._models.items()
            if key[0] != provider_name
        }

        for model in discovered_models:
            key = (provider_name, model.id)

            self._models[key] = CatalogModel(
                provider=provider_name,
                model=model
            )

        self._provider_errors.pop(provider_name, None)

        return discovered_models

    async def refresh_all(self):
        failures = {}

        for provider in self.registry.get_configured_providers():
            try:
                await self.refresh_provider(provider.name)

            except ProviderError as exc:
                failures[provider.name] = str(exc)
                self._provider_errors[provider.name] = str(exc)

        return {
            "models": self.get_all_models(),
            "failures": failures
        }

    def get_all_models(self) -> list[CatalogModel]:
        return list(self._models.values())

    def get_provider_models(
        self,
        provider_name: str
    ) -> list[CatalogModel]:

        return [
            item
            for item in self._models.values()
            if item.provider == provider_name
        ]

    def get_provider_errors(self) -> dict[str, str]:
        return self._provider_errors.copy()


model_catalog = ModelCatalog(provider_registry)