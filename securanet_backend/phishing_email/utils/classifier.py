from django.apps import apps
import logging
import hashlib
import datetime
import json
import os

def mask_sensitive(text):
    import re
    text = re.sub(r'([\w\.-]+)@([\w\.-]+)', r'***@\2', text)
    text = re.sub(r'(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})', r'***.***.***.\4', text)
    return text

logger = logging.getLogger(__name__)

def classify_header_text(text):
    """
    Classify email header text using the trained ML model.
    Logs prediction details for monitoring.
    """
    try:
        model = apps.get_app_config('myapp').model
        if model is None:
            logger.error("ML model not loaded")
            return {
                "label": "unknown",
                "confidence": 0.0,
                "error": "Model not available"
            }
        # Make prediction
        label = model.predict([text])[0]
        probabilities = model.predict_proba([text])[0]
        confidence = max(probabilities)
        # Advanced monitoring: log prediction
        header_hash = hashlib.sha256(text.encode()).hexdigest()
        log_entry = {
            'header_hash': header_hash,
            'prediction': label,
            'confidence': round(confidence, 2),
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'header_preview': mask_sensitive(text[:200])
        }
        log_path = os.path.join(os.path.dirname(__file__), 'prediction_logs.jsonl')
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        return {
            "label": label,
            "confidence": round(confidence, 2)
        }
    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        return {
            "label": "unknown",
            "confidence": 0.0,
            "error": f"Classification failed: {str(e)}"
        } 