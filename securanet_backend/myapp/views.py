#from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from transformers import pipeline

classifier = pipeline("text-classification", model="cybersectony/phishing-email-detection-distilbert_v2.4.1")

def classify_message(text):
    result = classifier(text)[0]
    label = result["label"]

    # Map model output to your custom labels
    verdict = "Suspicious" if label == "NEGATIVE" else "Not Suspicious"

    return {
        "verdict": verdict,
        "confidence": round(result["score"], 3)
    }

@api_view(['GET','POST'])
def check_phishing(request):
    message = request.data.get('message')
    if not message:
        return Response({"error": "No message provided"}, status = 400)
    
    prediction = classify_message(message)
    return Response(prediction)
