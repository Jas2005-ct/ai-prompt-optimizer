"""AI Provider Factory — central provider instantiation."""
from django.conf import settings
from apps.ai_providers.base import BaseAIProvider
from apps.ai_providers.providers import (
    OpenAIProvider, 
    AnthropicProvider, 
    GeminiProvider, 
    GroqProvider, 
    OpenRouterAI
)


PROVIDER_MAP = {
    'openai': OpenAIProvider,
    'anthropic': AnthropicProvider,
    'gemini': GeminiProvider,
    'groq': GroqProvider,
    'openrouter': OpenRouterAI,
}

MODEL_REGISTRY = {
    'gemini': {
        'id': 'gemini',
        'name': 'Gemini (Google)',
        'provider': 'gemini',
        'model_name': 'gemini-2.0-flash',
    },
    'openai': {
        'id': 'openai',
        'name': 'OpenAI (GPT-OSS)',
        'provider': 'openrouter',
        'model_name': 'openai/gpt-oss-120b:free',
    },
    'nvidia': {
        'id': 'nvidia',
        'name': 'Nvidia (Nemotron)',
        'provider': 'openrouter',
        'model_name': 'nvidia/nemotron-3-super-120b-a12b:free',
    },
    'meta': {
        'id': 'meta',
        'name': 'Llama 3 (Meta)',
        'provider': 'groq',
        'model_name': 'llama3-8b-8192',
    },
    'glm': {
        'id': 'glm',
        'name': 'GLM 4.5 (Z-AI)',
        'provider': 'openrouter',
        'model_name': 'z-ai/glm-4.5-air:free',
    }
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

    @staticmethod
    def list_available_models() -> list[dict]:
        """Return list of models whose provider has a configured API key."""
        available = []
        for model_id, info in MODEL_REGISTRY.items():
            provider_name = info['provider']
            cfg = settings.AI_PROVIDERS.get(provider_name)
            if cfg and cfg.get('api_key'):
                available.append({
                    'id': model_id,
                    'name': info['name'],
                })
        return available

