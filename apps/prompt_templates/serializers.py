from rest_framework import serializers
from .models import PromptTemplate


class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = ['id', 'title', 'description', 'category', 'template_text',
                  'example_input', 'tags', 'is_featured', 'use_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'use_count']
