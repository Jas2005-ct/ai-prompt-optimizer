from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.shared.utils import build_api_response
from .models import PromptTemplate
from .serializers import PromptTemplateSerializer


class TemplatesPageView(APIView):
    def get(self, request):
        templates = PromptTemplate.objects.all()
        return render(request, 'prompt_templates/templates.html', {'templates': templates})


class ListTemplatesAPIView(APIView):
    def get(self, request):
        category = request.query_params.get('category')
        qs = PromptTemplate.objects.all()
        if category:
            qs = qs.filter(category=category)
        serializer = PromptTemplateSerializer(qs, many=True)
        return Response(build_api_response(True, data=serializer.data))
