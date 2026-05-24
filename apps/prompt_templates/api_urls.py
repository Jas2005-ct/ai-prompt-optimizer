from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListTemplatesAPIView.as_view(), name='api-templates'),
]
