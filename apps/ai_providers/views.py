from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.ai_providers.factory import AIProviderFactory
from apps.shared.utils import build_api_response


class ListProvidersView(APIView):
    """List available (configured + active) AI providers."""

    def get(self, request):
        providers = AIProviderFactory.list_available_providers()
        return Response(build_api_response(True, data=providers))


class ListProviderModelsView(APIView):
    """
    List models for a specific provider or all providers.

    GET /api/providers/models/          -> all providers with models
    GET /api/providers/models/?provider=groq  -> models for groq only
    """

    def get(self, request):
        provider_name = request.query_params.get('provider')
        try:
            if provider_name:
                models = AIProviderFactory.list_models_for_provider(provider_name)
                data = {provider_name: models}
            else:
                data = AIProviderFactory.list_all_provider_models()
            return Response(build_api_response(True, data=data))
        except ValueError as e:
            return Response(
                build_api_response(False, error=str(e)),
                status=status.HTTP_400_BAD_REQUEST,
            )
