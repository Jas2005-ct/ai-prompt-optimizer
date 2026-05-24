from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.shared.utils import build_api_response
from .services import AnalyticsService


class AnalyticsPageView(APIView):
    def get(self, request):
        stats = AnalyticsService.get_overview_stats()
        chart_data = AnalyticsService.get_last_7_days()
        return render(request, 'analytics/analytics.html', {
            'stats': stats,
            'chart_data': chart_data,
        })


class AnalyticsStatsAPIView(APIView):
    def get(self, request):
        stats = AnalyticsService.get_overview_stats()
        chart = AnalyticsService.get_last_7_days()
        return Response(build_api_response(True, data={'stats': stats, 'chart': chart}))
