#from django.shortcuts import render

# Create your views here.
from rest_framework import api_view
from rest_framework.response import Response
from .models import clasify_message

@api_view(['POST'])
def check_phishing(request):
    message = request.data.get('message')
    if not message:
        return Response({"error": "No mesage provided"}, status = 400)
    
    prediction = clasify_message(message)
    return Response(prediction)
