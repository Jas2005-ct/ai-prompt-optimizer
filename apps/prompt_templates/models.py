"""Prompt Templates models."""
from django.db import models
from apps.shared.models import BaseModel


class PromptTemplate(BaseModel):
    """Pre-built prompt templates for various categories."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, default='general')
    template_text = models.TextField()
    example_input = models.TextField(blank=True)
    example_output = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    is_featured = models.BooleanField(default=False)
    use_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-is_featured', '-use_count', 'title']

    def __str__(self):
        return f"{self.category} | {self.title}"
