"""Analytics service for computing dashboard stats."""
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta


class AnalyticsService:
    """
    Computes real-time analytics from OptimizationRecord data.
    """

    @staticmethod
    def get_overview_stats() -> dict:
        from apps.prompt_optimizer.models import OptimizationRecord
        total = OptimizationRecord.objects.count()
        saved = OptimizationRecord.objects.filter(is_saved=True).count()
        today = timezone.now().date()
        today_count = OptimizationRecord.objects.filter(created_at__date=today).count()
        by_type = (
            OptimizationRecord.objects.values('prompt_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        by_provider = (
            OptimizationRecord.objects.values('ai_provider')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        total_tokens = OptimizationRecord.objects.aggregate(total=Sum('token_count'))['total'] or 0
        return {
            'total_optimizations': total,
            'saved_prompts': saved,
            'today_count': today_count,
            'by_type': list(by_type),
            'by_provider': list(by_provider),
            'total_tokens_used': total_tokens,
        }

    @staticmethod
    def get_last_7_days() -> list:
        from apps.prompt_optimizer.models import OptimizationRecord
        result = []
        today = timezone.now().date()
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = OptimizationRecord.objects.filter(created_at__date=day).count()
            result.append({'date': str(day), 'count': count})
        return result
