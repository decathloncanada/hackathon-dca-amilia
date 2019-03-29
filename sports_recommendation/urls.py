from django.urls import path
from .views import get_locations

urlpatterns = [
    path('', get_locations, name='locations'),
]
