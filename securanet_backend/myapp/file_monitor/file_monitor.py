from datetime import timedelta
from django.utils import timezone
from myapp.models import FileChangeLog
from decouple import config
import openai
import hashlib

openai.api_key = config('OPENAI_API_KEY')

recent_event_cache = {}

def analyze_file_risk(file_path, change_type):
    prompt = (
        f"Analyze this file event and classify it as 'safe', 'suspicious', or 'dangerous'. "
        f"File path: {file_path}\nChange type: {change_type}\n"
        f"Explain why and provide a recommended action."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a cybersecurity AI assistant that helps classify file events."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.lower()

        if "dangerous" in content:
            risk_level = "dangerous"
        elif "suspicious" in content:
            risk_level = "suspicious"
        else:
            risk_level = "safe"

        return risk_level, content.capitalize()

    except Exception as e:
        print(f"⚠️ OpenAI analysis failed: {e}")
        return "safe", "AI analysis failed, defaulting to safe. No action needed."

def log_file_change(file_path, change_type):
    now = timezone.now()
    rounded_timestamp = now.replace(microsecond=0)

    dedup_string = f"{file_path}-{change_type}-{rounded_timestamp.isoformat()}"
    dedup_key = hashlib.md5(dedup_string.encode()).hexdigest()

    # Check if entry with this dedup_key already exists
    if FileChangeLog.objects.filter(dedup_key=dedup_key).exists():
        print(f"⚠️ Skipped duplicate (dedup key): {dedup_key}")
        return

    risk_level, recommendation = analyze_file_risk(file_path, change_type)

    FileChangeLog.objects.create(
        file_path=file_path,
        change_type=change_type,
        risk_level=risk_level,
        recommendation=recommendation,
        dedup_key=dedup_key
    )
    print(f"✅ Logged event with dedup key: {dedup_key}")