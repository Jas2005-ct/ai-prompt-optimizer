from rest_framework.views import APIView
from rest_framework.response import Response
from apps.ai_providers.factory import AIProviderFactory
from apps.shared.utils import build_api_response


class ListProvidersView(APIView):
    """List available AI providers."""

    def get(self, request):
        providers = AIProviderFactory.list_available_providers()
        return Response(build_api_response(True, data=providers))
