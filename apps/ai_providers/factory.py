"""AI Provider Factory — central provider instantiation."""
from django.conf import settings
from apps.ai_providers.base import BaseAIProvider
from apps.ai_providers.providers import (
    OpenCodeZenProvider, OpenRouterProvider,
)


# ---------------------------------------------------------------------------
# Active provider map — only providers currently supported
# ---------------------------------------------------------------------------
PROVIDER_MAP = {
    'openrouter': OpenRouterProvider,
    'opencode_zen': OpenCodeZenProvider,
}


# ---------------------------------------------------------------------------
# Friendly display labels per provider (used in UI dropdowns / dashboard)
# ---------------------------------------------------------------------------
PROVIDER_LABELS = {
    'openrouter': 'OpenRouter',
    'opencode_zen': 'OpenCode Zen',
}


# ---------------------------------------------------------------------------
# Available models per provider (used for UI dropdowns / API listing)
# ---------------------------------------------------------------------------
PROVIDER_MODELS = {
    'openrouter': [
        {'id': 'nvidia/nemotron-3-ultra-550b-a55b:free', 'label': 'NVIDIA Nemotron Ultra 550B (Free)', 'default': True},
        {'id': 'inclusionai/ling-3.0-flash:free', 'label': 'Ling 3.0 Flash (Free)'},
        {'id': 'poolside/laguna-s-2.1:free', 'label': 'Laguna S 2.1 (Free)'},
        {'id': 'openai/gpt-oss-20b:free', 'label': 'GPT OSS 20B (Free)'},
    ],
    'opencode_zen': [
        {'id': 'gpt-5.4-mini', 'label': 'GPT 5.4 Mini', 'default': True},
        {'id': 'deepseek-v4-flash', 'label': 'DeepSeek V4 Flash'},
        {'id': 'deepseek-v4-flash-free', 'label': 'DeepSeek V4 Flash (Free)'},
        {'id': 'glm-5.1', 'label': 'GLM 5.1'},
        {'id': 'kimi-k2.5', 'label': 'Kimi K2.5'},
        {'id': 'big-pickle', 'label': 'Big Pickle (Free)'},
    ],
}


class AIProviderFactory:
    """
    Factory class to instantiate AI providers dynamically.
    Usage: provider = AIProviderFactory.get_provider_for_model('nvidia/nemotron-3-ultra-550b-a55b:free')
           provider = AIProviderFactory.get_provider('openrouter', model='openai/gpt-oss-20b:free')
    """

    @staticmethod
    def get_provider_for_model(model: str = None) -> str:
        """Return the provider key that owns the given model id."""
        if not model:
            return settings.DEFAULT_AI_PROVIDER
        for provider_name, models in PROVIDER_MODELS.items():
            if any(m['id'] == model for m in models):
                return provider_name
        raise ValueError(f"Model '{model}' is not available for any configured provider.")

    @staticmethod
    def get_provider(provider_name: str = None, model: str = None) -> BaseAIProvider:
        """Return an instantiated provider based on name (derived from model if omitted)."""
        provider_name = provider_name or AIProviderFactory.get_provider_for_model(model)
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
    def list_available_providers_with_labels() -> list:
        """Return list of dicts {id, label} for configured providers."""
        return [
            {'id': name, 'label': PROVIDER_LABELS.get(name, name)}
            for name in AIProviderFactory.list_available_providers()
        ]

    @staticmethod
    def list_available_models() -> list:
        """Return flat list of dicts {id, label, provider, provider_label} for configured providers."""
        models = []
        for provider_name in AIProviderFactory.list_available_providers():
            for m in PROVIDER_MODELS.get(provider_name, []):
                models.append({
                    'id': m['id'],
                    'label': m['label'],
                    'provider': provider_name,
                    'provider_label': PROVIDER_LABELS.get(provider_name, provider_name),
                    'default': m.get('default', False),
                })
        return models

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
