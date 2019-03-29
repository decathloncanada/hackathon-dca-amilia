from django.urls import path
from .views import get_sports_activities

urlpatterns = [
    path('', get_sports_activities, name='locations'),
]
