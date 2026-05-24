"""Models for prompt optimization history and saved prompts."""
from django.db import models
from apps.shared.models import BaseModel


class PromptType(models.TextChoices):
    GENERAL = 'general', 'General AI'
    CODING = 'coding', 'Coding'
    SQL = 'sql', 'SQL'
    UIUX = 'uiux', 'UI/UX'
    IMAGE = 'image', 'Image Generation'
    API = 'api', 'API Generation'
    DEVOPS = 'devops', 'DevOps'
    DOCUMENTATION = 'documentation', 'Documentation'
    ARCHITECTURE = 'architecture', 'Architecture'


class OptimizationRecord(BaseModel):
    """Stores a single prompt optimization request and result."""
    raw_prompt = models.TextField(help_text='Original user-entered prompt')
    prompt_type = models.CharField(
        max_length=50,
        choices=PromptType.choices,
        default=PromptType.GENERAL,
    )
    ai_provider = models.CharField(max_length=50, default='openai')
    ai_model = models.CharField(max_length=100, blank=True)

    # Results
    optimized_prompt = models.TextField(blank=True)
    suggested_role = models.TextField(blank=True)
    improvements_made = models.JSONField(default=list)
    output_structure = models.TextField(blank=True)
    token_count = models.IntegerField(default=0)

    # Metadata
    session_id = models.CharField(max_length=100, blank=True, db_index=True)
    is_saved = models.BooleanField(default=False)
    rating = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Optimization Record'
        verbose_name_plural = 'Optimization Records'
        indexes = [
            models.Index(fields=['prompt_type']),
            models.Index(fields=['ai_provider']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.prompt_type} | {self.raw_prompt[:50]}..."


class SavedPrompt(BaseModel):
    """User-saved optimized prompts."""
    title = models.CharField(max_length=200)
    prompt_type = models.CharField(max_length=50, choices=PromptType.choices)
    optimized_prompt = models.TextField()
    suggested_role = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    optimization_record = models.OneToOneField(
        OptimizationRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='saved_prompt',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Saved Prompt'
        verbose_name_plural = 'Saved Prompts'

    def __str__(self):
        return self.title
