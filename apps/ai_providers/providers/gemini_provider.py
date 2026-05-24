"""Google Gemini provider implementation."""
from tenacity import retry, stop_after_attempt, wait_exponential
from apps.ai_providers.base import BaseAIProvider, AIResponse
from apps.shared.exceptions import AIProviderException


class GeminiProvider(BaseAIProvider):
    """Google Gemini provider."""

    @property
    def provider_name(self) -> str:
        return 'gemini'

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def complete(self, system_prompt: str, user_prompt: str, **kwargs) -> AIResponse:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_prompt,
            )
            response = model.generate_content(user_prompt)
            return AIResponse(
                content=response.text,
                provider=self.provider_name,
                model=self.model,
                total_tokens=getattr(response.usage_metadata, 'total_token_count', 0),
            )
        except Exception as e:
            raise AIProviderException('gemini', str(e))
