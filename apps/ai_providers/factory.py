"""AI Provider Factory — central provider instantiation."""
from django.conf import settings
from apps.ai_providers.base import BaseAIProvider
from apps.ai_providers.providers import (
    OpenAIProvider, AnthropicProvider, GeminiProvider, GroqProvider
)


PROVIDER_MAP = {
    'openai': OpenAIProvider,
    'anthropic': AnthropicProvider,
    'gemini': GeminiProvider,
    'groq': GroqProvider,
}


class AIProviderFactory:
    """
    Factory class to instantiate AI providers dynamically.
    Usage: provider = AIProviderFactory.get_provider('openai')
    """

    @staticmethod
    def get_provider(provider_name: str = None, model: str = None) -> BaseAIProvider:
        """Return an instantiated provider based on name."""
        provider_name = provider_name or settings.DEFAULT_AI_PROVIDER
        config = settings.AI_PROVIDERS.get(provider_name)

        if not config:
            raise ValueError(f"Unknown AI provider: {provider_name}")

        provider_class = PROVIDER_MAP.get(provider_name)
        if not provider_class:
            raise ValueError(f"No implementation found for provider: {provider_name}")

        return provider_class(
            api_key=config['api_key'],
            model=model or config['default_model'],
            timeout=config.get('timeout', 30),
            max_retries=config.get('max_retries', 3),
        )

    @staticmethod
    def list_available_providers() -> list:
        """Return list of configured providers (with non-empty API keys)."""
        return [
            name
            for name, cfg in settings.AI_PROVIDERS.items()
            if cfg.get('api_key')
        ]
