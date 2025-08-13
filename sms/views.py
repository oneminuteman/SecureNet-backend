from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MessageAnalysis, Feedback
from .serializers import FeedbackSerializer

THREAT_KEYWORDS = ["bomb", "kill", "danger", "attack", "alert", "threat"]

@api_view(['POST'])
def analyze_message(request):
    message = request.data.get("message")
    if not message:
        return Response({"error": "Message is required"}, status=400)

    is_threat = any(word in message.lower() for word in THREAT_KEYWORDS)
    threat_type = "Threat" if is_threat else "Safe"

    analysis = MessageAnalysis.objects.create(original_message=message, result=threat_type)

    return Response({
        "id": analysis.id,
        "message": analysis.original_message,
        "threat_type": analysis.result
    })


@api_view(['POST'])
def submit_feedback(request):
    serializer = FeedbackSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response({"error": "Invalid feedback data", "details": serializer.errors}, status=400)


@api_view(['GET'])
def feedback_history(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    serializer = FeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)
