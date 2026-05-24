from django.urls import path
from . import views

urlpatterns = [
    path('', views.OptimizerPageView.as_view(), name='optimizer'),
    path('history/', views.HistoryPageView.as_view(), name='history'),
]
