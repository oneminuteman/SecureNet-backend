from django.urls import path
from django.http import JsonResponse
from .views import analyze_email_header, analyze_header

def api_info(request):
    """API information endpoint"""
    return JsonResponse({
        "name": "SecuraNet Email Header Analyzer API",
        "version": "1.0.0",
        "description": "API for analyzing email headers with ML classification",
        "endpoints": {
            "analyze": "/analyze/",
            "analyze_header": "/analyze-header/"
        },
        "documentation": "/swagger/"
    })

urlpatterns = [
    path('', api_info, name='api_info'),
    path('analyze/', analyze_email_header, name='analyze_email_header'),
    path('analyze-header/', analyze_header, name='analyze_header'),
]
