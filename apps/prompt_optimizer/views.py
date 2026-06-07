"""Views for Prompt Optimizer — both HTML and API."""
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.ai_providers.factory import AIProviderFactory
from apps.shared.utils import build_api_response
from apps.shared.exceptions import PromptOptimizationException

from .models import OptimizationRecord, SavedPrompt
from .serializers import (
    OptimizePromptInputSerializer,
    OptimizationRecordSerializer,
    SavedPromptSerializer,
    SavePromptInputSerializer,
)
from .services import PromptOptimizationService


class OptimizerPageView(APIView):
    """Main optimizer HTML page."""

    def get(self, request):
        models = AIProviderFactory.list_available_models()
        # Find default model: if 'openai' is available, use it, otherwise the first available
        default_model = 'openai' if any(m['id'] == 'openai' for m in models) else (models[0]['id'] if models else '')
        context = {
            'models': models,
            'prompt_types': OptimizationRecord.prompt_type.field.choices if hasattr(OptimizationRecord, 'prompt_type') else [],
            'default_model': default_model,
        }
        return render(request, 'prompt_optimizer/optimizer.html', context)



class OptimizePromptAPIView(APIView):
    """API: Optimize a raw prompt."""

    def post(self, request):
        serializer = OptimizePromptInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                build_api_response(False, message='Invalid input', data=serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        service = PromptOptimizationService(
            provider_name=data.get('provider'),
            model=data.get('model'),
        )
        try:
            result = service.optimize(
                raw_prompt=data['raw_prompt'],
                prompt_type=data.get('prompt_type', 'general'),
                session_id=data.get('session_id', ''),
            )
            return Response(build_api_response(True, data=result))
        except PromptOptimizationException as e:
            return Response(
                build_api_response(False, message=str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OptimizationHistoryAPIView(APIView):
    """API: Fetch optimization history."""

    def get(self, request):
        records = OptimizationRecord.objects.all()[:50]
        serializer = OptimizationRecordSerializer(records, many=True)
        return Response(build_api_response(True, data=serializer.data))


class SavePromptAPIView(APIView):
    """API: Save an optimized prompt."""

    def post(self, request):
        serializer = SavePromptInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                build_api_response(False, data=serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )
        data = serializer.validated_data
        record = get_object_or_404(OptimizationRecord, id=data['optimization_id'])
        saved = SavedPrompt.objects.create(
            title=data['title'],
            prompt_type=record.prompt_type,
            optimized_prompt=record.optimized_prompt,
            suggested_role=record.suggested_role,
            tags=data.get('tags', []),
            optimization_record=record,
        )
        record.is_saved = True
        record.save(update_fields=['is_saved'])
        return Response(build_api_response(True, data=SavedPromptSerializer(saved).data))


class HistoryPageView(APIView):
    """HTML: Optimization history page."""

    def get(self, request):
        records = OptimizationRecord.objects.all()[:100]
        return render(request, 'prompt_optimizer/history.html', {'records': records})
