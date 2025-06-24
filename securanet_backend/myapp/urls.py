from django.urls import path
from .views import check_phishing

url_patterns = [
    path('classify-message/', check_phishing),
]