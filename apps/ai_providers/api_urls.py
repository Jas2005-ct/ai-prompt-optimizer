from django.urls import path
from apps.ai_providers.views import ListProvidersView, ListProviderModelsView

urlpatterns = [
    path('providers/', ListProvidersView.as_view(), name='list-providers'),
    path('providers/models/', ListProviderModelsView.as_view(), name='list-provider-models'),
]
