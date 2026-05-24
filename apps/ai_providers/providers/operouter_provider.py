from tenacity import retry, stop_after_attempt, wait_exponential
from apps.ai_providers.base import BaseAIProvider, AIResponse
from apps.shared.exceptions import AIProviderException


class OpenRouterAI(BaseAIProvider):

    @property
    def provider_name(self) -> str:
        return 'operouter'
    

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
                raise AIProviderException('operouter', response_json.get('error', {}).get('message', 'Unknown error'))

            return AIResponse(
                content=response_json['choices'][0]['message']['content'],
                provider=self.provider_name,
                model=self.model,
                prompt_tokens=response_json['usage']['prompt_tokens'],
                completion_tokens=response_json['usage']['completion_tokens'],
                total_tokens=response_json['usage']['total_tokens'],
            )
        except Exception as e:
            raise AIProviderException('operouter', str(e))