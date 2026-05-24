"""Abstract base class for all AI providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class AIResponse:
    """Standardized response from any AI provider."""
    content: str
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    success: bool = True
    error: Optional[str] = None


class BaseAIProvider(ABC):
    """
    Abstract base class for all AI provider integrations.
    Each provider must implement `complete()`.
    """

    def __init__(self, api_key: str, model: str, timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str, **kwargs) -> AIResponse:
        """Send a prompt to the AI provider and return a standardized response."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier string."""
        pass
