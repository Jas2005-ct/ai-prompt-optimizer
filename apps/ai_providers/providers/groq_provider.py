"""Groq provider implementation."""
from tenacity import retry, stop_after_attempt, wait_exponential
from apps.ai_providers.base import BaseAIProvider, AIResponse
from apps.shared.exceptions import AIProviderException


class GroqProvider(BaseAIProvider):
    """Groq provider (ultra-fast inference)."""

    @property
    def provider_name(self) -> str:
        return 'groq'

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def complete(self, system_prompt: str, user_prompt: str, **kwargs) -> AIResponse:
        try:
            from groq import Groq
            client = Groq(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2000),
            )
            usage = response.usage
            return AIResponse(
                content=response.choices[0].message.content,
                provider=self.provider_name,
                model=self.model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
            )
        except Exception as e:
            raise AIProviderException('groq', str(e))
