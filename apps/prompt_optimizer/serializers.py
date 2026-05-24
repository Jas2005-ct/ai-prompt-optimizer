"""DRF serializers for prompt optimizer."""
from rest_framework import serializers
from .models import OptimizationRecord, SavedPrompt


class OptimizePromptInputSerializer(serializers.Serializer):
    """Validates incoming optimization requests."""
    raw_prompt = serializers.CharField(
        min_length=5,
        max_length=5000,
        error_messages={
            'min_length': 'Prompt must be at least 5 characters.',
            'max_length': 'Prompt cannot exceed 5000 characters.',
        }
    )
    prompt_type = serializers.ChoiceField(
        choices=['general', 'coding', 'sql', 'uiux', 'image', 'api', 'devops', 'documentation', 'architecture'],
        default='general',
    )
    provider = serializers.CharField(max_length=50, default='openai')
    model = serializers.CharField(max_length=100, required=False, allow_blank=True)
    session_id = serializers.CharField(max_length=100, required=False, allow_blank=True)


class OptimizationRecordSerializer(serializers.ModelSerializer):
    """Full serializer for optimization records."""
    class Meta:
        model = OptimizationRecord
        fields = [
            'id', 'raw_prompt', 'prompt_type', 'ai_provider', 'ai_model',
            'optimized_prompt', 'suggested_role', 'improvements_made',
            'output_structure', 'token_count', 'is_saved', 'rating', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class SavedPromptSerializer(serializers.ModelSerializer):
    """Serializer for saved prompts."""
    class Meta:
        model = SavedPrompt
        fields = ['id', 'title', 'prompt_type', 'optimized_prompt', 'suggested_role', 'tags', 'created_at']
        read_only_fields = ['id', 'created_at']


class SavePromptInputSerializer(serializers.Serializer):
    """Validates save prompt requests."""
    optimization_id = serializers.UUIDField()
    title = serializers.CharField(max_length=200)
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)
