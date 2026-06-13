from rest_framework.views import APIView
from rest_framework.response import Response
from apps.ai_providers.factory import AIProviderFactory
from apps.shared.utils import build_api_response


class ListProvidersView(APIView):
    """List available AI providers."""

    def get(self, request):
        providers = AIProviderFactory.list_available_providers()
        return Response(build_api_response(True, data=providers))


class SwitchModelAPIView(APIView):
    """API: Switch default AI model in session."""

    def post(self, request):
        provider = request.data.get('provider')
        model = request.data.get('model')
        if not provider:
            return Response(
                build_api_response(False, message='Provider name is required'),
                status=400
            )
        request.session['default_provider'] = provider
        if model:
            request.session['default_model'] = model
        return Response(
            build_api_response(
                True, 
                message=f'Default model switched to {provider} successfully.'
            )
        )
