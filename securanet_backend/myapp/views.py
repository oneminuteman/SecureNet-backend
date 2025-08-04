#from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from pathlib import Path

# ✅ Fix: Use Path and resolve to POSIX style for compatibility
MODEL_PATH = Path(__file__).resolve().parent.parent / "phishing_model"
MODEL_PATH = MODEL_PATH.as_posix()  # ✅ Converts to forward-slash format

# ✅ Load local tokenizer and model
from transformers import AutoConfig

# 🛠️ Load config manually first to avoid HFValidationError
config = AutoConfig.from_pretrained(MODEL_PATH, local_files_only=True)

# ✅ Then load tokenizer and model using config
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, config=config, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, config=config, local_files_only=True)

# ✅ Create pipeline
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

def classify_message(text):
    result = classifier(text)[0]
    label = result["label"].lower()
    verdict = "suspicious" if label == "phishing" else "not suspicious"
    confidence = round(result["score"], 3)
    return {
        "verdict": verdict,
        "confidence": confidence
    }

@api_view(['POST'])
def check_phishing(request):
    message = request.data.get('message')
    if not message:
        return Response({"error": "No message provided"}, status=400)
    prediction = classify_message(message)
    return Response(prediction)
