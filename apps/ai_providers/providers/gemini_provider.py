"""Google Gemini provider implementation (google-genai SDK)."""
from tenacity import retry, stop_after_attempt, wait_exponential
from apps.ai_providers.base import BaseAIProvider, AIResponse
from apps.shared.exceptions import AIProviderException


class GeminiProvider(BaseAIProvider):
    """Google Gemini provider using the new google-genai SDK."""

    @property
    def provider_name(self) -> str:
        return 'gemini'

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def complete(self, system_prompt: str, user_prompt: str, **kwargs) -> AIResponse:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=kwargs.get('temperature', 0.7),
                    max_output_tokens=kwargs.get('max_tokens', 2000),
                ),
            )
            return AIResponse(
                content=response.text,
                provider=self.provider_name,
                model=self.model,
                total_tokens=getattr(response.usage_metadata, 'total_token_count', 0),
            )
        except Exception as e:
            raise AIProviderException('gemini', str(e))
