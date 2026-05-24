from django.urls import path
from . import views

urlpatterns = [
    path('', views.TemplatesPageView.as_view(), name='templates'),
]
