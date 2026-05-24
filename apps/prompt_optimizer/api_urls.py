from django.urls import path
from . import views

urlpatterns = [
    path('', views.OptimizePromptAPIView.as_view(), name='api-optimize'),
    path('history/', views.OptimizationHistoryAPIView.as_view(), name='api-history'),
    path('save/', views.SavePromptAPIView.as_view(), name='api-save'),
]
