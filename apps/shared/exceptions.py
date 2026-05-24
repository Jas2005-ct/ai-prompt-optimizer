"""Custom exception handlers and exceptions."""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """Centralized DRF exception handler with standardized response format."""
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            'success': False,
            'error': response.data,
            'status_code': response.status_code,
        }
    return response


class AIProviderException(Exception):
    """Raised when an AI provider call fails."""
    def __init__(self, provider: str, message: str):
        self.provider = provider
        self.message = message
        super().__init__(f"[{provider}] {message}")


class PromptOptimizationException(Exception):
    """Raised when prompt optimization pipeline fails."""
    pass
