from django.urls import path
from . import views

urlpatterns = [
    path('', views.AnalyticsPageView.as_view(), name='analytics'),
]
