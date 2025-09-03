from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
import json

# ✅ HuggingFace imports
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer, AutoConfig

# ✅ Load phishing model (local)
MODEL_PATH = Path(__file__).resolve().parent / "phishing_model"
MODEL_PATH = MODEL_PATH.as_posix()

classifier = None
try:
    config = AutoConfig.from_pretrained(MODEL_PATH, local_files_only=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, config=config, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, config=config, local_files_only=True)
    classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)
except Exception as e:
    print(f"[WARNING] Could not load phishing model. Using mock classifier. Error: {e}")


def run_classification(text: str):
    """
    Unified classifier: uses HuggingFace model if available,
    otherwise falls back to rule-based detection.
    """
    if classifier:
        result = classifier(text)[0]
        label = result["label"].lower()
        verdict = "suspicious" if label == "phishing" else "not suspicious"
        confidence = round(result["score"], 3)
        return {"verdict": verdict, "confidence": confidence}
    else:
        # Mock fallback
        if "bank" in text.lower():
            return {"verdict": "suspicious", "confidence": 0.8}
        return {"verdict": "not suspicious", "confidence": 0.9}


@api_view(['POST'])
def check_phishing(request):
    """
    DRF endpoint: /api/phishing/check/
    Accepts JSON { "message": "..." }
    """
    message = request.data.get("message")
    if not message:
        return Response({"error": "No message provided"}, status=400)

    prediction = run_classification(message)
    return Response(prediction)


@csrf_exempt
def classify_message(request):
    """
    Raw Django endpoint (non-DRF) for flexibility
    /api/classify-message/
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            if not message:
                return JsonResponse({"error": "No message provided"}, status=400)

            prediction = run_classification(message)
            return JsonResponse({"status": "ok", **prediction})

        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)
