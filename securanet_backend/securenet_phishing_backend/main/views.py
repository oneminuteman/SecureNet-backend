from django.http import JsonResponse
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PhishingLog
from .serializers import PhishingLogSerializer

# Example accepted credentials dictionary
ACCEPTED_CREDENTIALS = {
    # "admin@example.com": {"password": "adminpass", "role": "admin"},
    "admin@secureNetAI.com": {"password": "supersecretekey", "role": "admin"},
}

@api_view(['GET', 'POST'])
def phishing_log_list_create(request):
    print(request)
    if request.method == 'GET':
        logs = PhishingLog.objects.all().order_by('-timestamp')
        serializer = PhishingLogSerializer(logs, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')
        creds = ACCEPTED_CREDENTIALS.get(email)
        print(email, password, creds)

        if email and password:
            if creds and creds['password'] == password:
                # Return role and email
                return JsonResponse({
                    "user": {
                        "success": True,
                        "role": creds['role'],
                        "email": email
                    }
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    "user": {
                        "success": False,
                        "role": "user",
                        "email": email
                    }
                }, status=status.HTTP_200_OK)
        else:
            # Normal user or invalid credentials
            return JsonResponse({"success": False}, status=status.HTTP_200_OK)
