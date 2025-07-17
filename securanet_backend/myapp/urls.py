from django.urls import path
from .views import check_phishing

urlpatterns = [
    path('api/classify-message/',check_phishing),
]