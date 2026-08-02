"""Template filters for AI providers."""
from django import template
from apps.ai_providers.factory import PROVIDER_LABELS

register = template.Library()


@register.filter
def provider_label(provider_name: str) -> str:
    """Return the friendly display label for a provider key."""
    return PROVIDER_LABELS.get(provider_name, provider_name or '—')
