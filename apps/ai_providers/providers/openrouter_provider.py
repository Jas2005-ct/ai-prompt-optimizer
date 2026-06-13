from tenacity import retry, stop_after_attempt, wait_exponential
from apps.ai_providers.base import BaseAIProvider, AIResponse
from apps.shared.exceptions import AIProviderException


class OpenRouterAI(BaseAIProvider):

    @property
    def provider_name(self) -> str:
        return 'openrouter'
    
    @property
    def model_name(self) -> list[str]:
        models = ['nvidia/nemotron-3-super-120b-a12b:free','z-ai/glm-4.5-air:free','openai/gpt-oss-120b:free']
        return models

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def complete(self, system_prompt: str, user_prompt: str, **kwargs) -> AIResponse:
        try:
            import requests
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": kwargs.get('temperature', 0.7),
                "max_tokens": kwargs.get('max_tokens', 2000),
            }

            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response_json = response.json()

            if response.status_code != 200:
                raise AIProviderException('openrouter', response_json.get('error', {}).get('message', 'Unknown error'))

            return AIResponse(
                content=response_json['choices'][0]['message']['content'],
                provider=self.provider_name,
                model=self.model,
                prompt_tokens=response_json.get('usage', {}).get('prompt_tokens', 0),
                completion_tokens=response_json.get('usage', {}).get('completion_tokens', 0),
                total_tokens=response_json.get('usage', {}).get('total_tokens', 0),
            )
        except Exception as e:
            raise AIProviderException('openrouter', str(e))
