"""Base models with shared fields."""
from django.db import models
import uuid


class BaseModel(models.Model):
    """Abstract base model with UUID PK, timestamps."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} ({self.id})"
