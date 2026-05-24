from django.shortcuts import render
from apps.analytics.services import AnalyticsService
from apps.ai_providers.factory import AIProviderFactory
from apps.prompt_optimizer.models import OptimizationRecord


def home_view(request):
    """Main dashboard/home page."""
    stats = AnalyticsService.get_overview_stats()
    recent = OptimizationRecord.objects.all()[:5]
    providers = AIProviderFactory.list_available_providers()
    return render(request, 'dashboard/home.html', {
        'stats': stats,
        'recent_optimizations': recent,
        'providers': providers,
    })
