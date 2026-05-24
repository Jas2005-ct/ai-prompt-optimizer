"""API URL configuration."""
from django.urls import path, include

urlpatterns = [
    path('optimize/', include('apps.prompt_optimizer.api_urls')),
    path('templates/', include('apps.prompt_templates.api_urls')),
    path('analytics/', include('apps.analytics.api_urls')),
    path('providers/', include('apps.ai_providers.api_urls')),
]
