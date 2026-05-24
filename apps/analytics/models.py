"""Analytics models for tracking usage."""
from django.db import models
from apps.shared.models import BaseModel


class DailyUsageStat(BaseModel):
    """Aggregated daily usage statistics."""
    date = models.DateField(unique=True)
    total_optimizations = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    optimizations_by_type = models.JSONField(default=dict)
    optimizations_by_provider = models.JSONField(default=dict)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Stats for {self.date}"
