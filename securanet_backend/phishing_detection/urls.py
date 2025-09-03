# phishing_detection/urls.py
from django.urls import path
from .views import classify_message, check_phishing

urlpatterns = [
    path("classify-message/", classify_message, name="classify-message"),
    path("check/", check_phishing, name="check-phishing"),
]
