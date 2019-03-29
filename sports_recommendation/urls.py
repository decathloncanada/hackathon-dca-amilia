from django.urls import path
from .views import test

app_name = "sports_recommendation"

urlpatterns = [
    path('', test, name='sports_reco_view'),
]
