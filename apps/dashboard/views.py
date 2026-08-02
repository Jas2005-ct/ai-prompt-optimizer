from django.shortcuts import render
from apps.analytics.services import AnalyticsService
from apps.ai_providers.factory import AIProviderFactory
from apps.prompt_optimizer.models import OptimizationRecord


def home_view(request):
    """Main dashboard/home page."""
    stats = AnalyticsService.get_overview_stats()
    recent = OptimizationRecord.objects.all()[:5]
    model_options = AIProviderFactory.list_available_models()
    return render(request, 'dashboard/home.html', {
        'stats': stats,
        'recent_optimizations': recent,
        'model_options': model_options,
    })
