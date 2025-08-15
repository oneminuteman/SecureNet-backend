from django.urls import path
from .views import check_phishing

urlpatterns = [
    path('classify-message/',check_phishing),
]