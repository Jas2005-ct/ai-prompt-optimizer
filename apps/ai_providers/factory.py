"""AI Provider Factory — central provider instantiation."""
from django.conf import settings
from apps.ai_providers.base import BaseAIProvider
from apps.ai_providers.providers import (
    GeminiProvider, GroqProvider, OpenRouterProvider,
    # Future providers (keep files, activate by adding here):
    # OpenAIProvider, AnthropicProvider,
)


# ---------------------------------------------------------------------------
# Active provider map — only providers currently supported
# ---------------------------------------------------------------------------
PROVIDER_MAP = {
    'gemini': GeminiProvider,
    'groq': GroqProvider,
    'openrouter': OpenRouterProvider,
    # 'openai': OpenAIProvider,       # future
    # 'anthropic': AnthropicProvider,  # future
}


# ---------------------------------------------------------------------------
# Available models per provider (used for UI dropdowns / API listing)
# ---------------------------------------------------------------------------
PROVIDER_MODELS = {
    'gemini': [
        {'id': 'gemini-2.0-flash', 'label': 'Gemini 2.0 Flash', 'default': True},
        {'id': 'gemini-2.0-flash-lite', 'label': 'Gemini 2.0 Flash Lite'},
        {'id': 'gemini-1.5-pro', 'label': 'Gemini 1.5 Pro'},
        {'id': 'gemini-1.5-flash', 'label': 'Gemini 1.5 Flash'},
    ],
    'groq': [
        {'id': 'llama-3.1-8b-instant', 'label': 'LLaMA 3.1 8B Instant', 'default': True},
        {'id': 'compound-beta', 'label': 'Groq Compound Beta'},
    ],
    'openrouter': [
        {'id': 'nvidia/nemotron-3-ultra-550b-a55b:free', 'label': 'NVIDIA Nemotron Ultra 550B (Free)', 'default': True},
        {'id': 'qwen/qwen3-next-80b-a3b-instruct:free', 'label': 'Qwen3 Next 80B Instruct (Free)'},
    ],
}


class AIProviderFactory:
    """
    Factory class to instantiate AI providers dynamically.
    Usage: provider = AIProviderFactory.get_provider('gemini')
           provider = AIProviderFactory.get_provider('groq', model='llama-3.1-8b-instant')
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
            raise ValueError(f"No active implementation for provider: {provider_name}")

        # Validate model belongs to this provider if explicitly passed
        if model:
            valid_ids = [m['id'] for m in PROVIDER_MODELS.get(provider_name, [])]
            if valid_ids and model not in valid_ids:
                raise ValueError(
                    f"Model '{model}' is not available for provider '{provider_name}'. "
                    f"Valid models: {valid_ids}"
                )

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
            if cfg.get('api_key') and name in PROVIDER_MAP
        ]

    @staticmethod
    def list_models_for_provider(provider_name: str) -> list:
        """Return the list of available models for a given provider."""
        if provider_name not in PROVIDER_MAP:
            raise ValueError(f"Unknown or inactive provider: {provider_name}")
        return PROVIDER_MODELS.get(provider_name, [])

    @staticmethod
    def list_all_provider_models() -> dict:
        """Return all providers with their available models."""
        return {
            provider: PROVIDER_MODELS.get(provider, [])
            for provider in PROVIDER_MAP
        }
