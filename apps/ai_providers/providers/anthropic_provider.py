"""Anthropic Claude provider implementation."""
from tenacity import retry, stop_after_attempt, wait_exponential
from apps.ai_providers.base import BaseAIProvider, AIResponse
from apps.shared.exceptions import AIProviderException


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude provider."""

    @property
    def provider_name(self) -> str:
        return 'anthropic'

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def complete(self, system_prompt: str, user_prompt: str, **kwargs) -> AIResponse:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 2000),
                system=system_prompt,
                messages=[{'role': 'user', 'content': user_prompt}],
            )
            return AIResponse(
                content=response.content[0].text,
                provider=self.provider_name,
                model=self.model,
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            )
        except Exception as e:
            raise AIProviderException('anthropic', str(e))
