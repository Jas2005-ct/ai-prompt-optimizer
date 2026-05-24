from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.ListProvidersView.as_view(), name='api-list-providers'),
]
