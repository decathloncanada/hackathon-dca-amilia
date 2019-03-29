from django.urls import path
from .views import get_activities

urlpatterns = [
    path('sports/', get_activities, name='locations'),
]
