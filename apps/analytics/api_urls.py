from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.AnalyticsStatsAPIView.as_view(), name='api-analytics'),
]
