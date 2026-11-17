from app.ai.router.provider_registry import provider_registry
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.groq_provider import GroqProvider

def initialize_providers():
    """Register all available provider integrations."""
    
    registered = provider_registry.get_registered_provider_names()
    
    if "gemini" not in registered:
        provider_registry.register(GeminiProvider())

    if "groq" not in registered:
        provider_registry.register(GroqProvider())    

    return provider_registry
    