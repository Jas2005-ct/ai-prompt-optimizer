from django.contrib import admin
from .models import OptimizationRecord, SavedPrompt


@admin.register(OptimizationRecord)
class OptimizationRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'prompt_type', 'ai_provider', 'ai_model', 'token_count', 'is_saved', 'created_at']
    list_filter = ['prompt_type', 'ai_provider', 'is_saved']
    search_fields = ['raw_prompt', 'optimized_prompt']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(SavedPrompt)
class SavedPromptAdmin(admin.ModelAdmin):
    list_display = ['title', 'prompt_type', 'created_at']
    list_filter = ['prompt_type']
    search_fields = ['title', 'optimized_prompt']
