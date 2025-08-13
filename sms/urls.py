from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_message),
    path('feedback/', views.submit_feedback),
    path('feedback/history/', views.feedback_history),
]
