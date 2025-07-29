from datetime import timedelta
from django.utils import timezone
from myapp.models import FileChangeLog
from decouple import config
import openai
import hashlib
import os
import mimetypes
import logging

logger = logging.getLogger(__name__)

# Initialize API key if available
try:
    openai.api_key = config('OPENAI_API_KEY', default='')
    USE_OPENAI = config('USE_OPENAI_ANALYSIS', default='true').lower() == 'true'
except Exception as e:
    logger.warning(f"Failed to initialize OpenAI: {e}")
    USE_OPENAI = False

# Cache for analyzed file types to reduce API calls
extension_risk_cache = {}
recent_event_cache = {}

def analyze_file_risk(file_path, change_type):
    """Analyze file risk with caching to reduce API calls"""
    # Skip analysis for very large files
    if os.path.exists(file_path):
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                return "suspicious", "File is too large for analysis. Manual review recommended."
        except Exception as e:
            logger.error(f"Error checking file size: {e}")
    
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Check cache for known extension risk levels
    if ext in extension_risk_cache:
        cached_result = extension_risk_cache[ext]
        return cached_result[0], cached_result[1]
    
    # Known safe extensions don't need API calls
    safe_extensions = ['.txt', '.csv', '.md', '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.docx', '.xlsx', '.pptx']
    if ext in safe_extensions and change_type != 'deleted':
        extension_risk_cache[ext] = ('safe', f"File with {ext} extension is generally safe. No action needed.")
        return 'safe', f"File with {ext} extension is generally safe. No action needed."
    
    # Known suspicious extensions don't need API calls
    suspicious_extensions = ['.exe', '.bat', '.ps1', '.vbs', '.js', '.dll', '.sh', '.py', '.rb', '.php']
    if ext in suspicious_extensions:
        extension_risk_cache[ext] = ('suspicious', 
                                   f"File with {ext} extension may pose a security risk. Verify source before running.")
        return 'suspicious', f"File with {ext} extension may pose a security risk. Verify source before running."
    
    # Known dangerous extensions don't need API calls
    dangerous_extensions = ['.locked', '.encrypted', '.ransomware', '.crypt', '.crypted', '.r5a', '.abc', '.aaa']
    if ext in dangerous_extensions:
        extension_risk_cache[ext] = ('dangerous', 
                                   f"File with {ext} extension is likely malicious. Quarantine immediately.")
        return 'dangerous', f"File with {ext} extension is likely malicious. Quarantine immediately."

    # Use local mimetype detection to further reduce API calls
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith('image/') or mime_type.startswith('audio/') or mime_type.startswith('video/'):
                extension_risk_cache[ext] = ('safe', f"File with MIME type {mime_type} is generally safe.")
                return 'safe', f"File with MIME type {mime_type} is generally safe."
            elif mime_type.startswith('application/x-executable') or mime_type.startswith('application/x-dosexec'):
                extension_risk_cache[ext] = ('suspicious', f"File with MIME type {mime_type} may be executable. Verify before running.")
                return 'suspicious', f"File with MIME type {mime_type} may be executable. Verify before running."
    except Exception as e:
        logger.warning(f"Error determining MIME type: {e}")

    # Fallback to AI analysis for unknown cases
    if USE_OPENAI and openai.api_key:
        try:
            prompt = (
                f"Analyze this file event and classify it as 'safe', 'suspicious', or 'dangerous'. "
                f"File path: {file_path}\nChange type: {change_type}\n"
                f"Explain why and provide a recommended action."
            )

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
                
            # Cache the result for this extension
            extension_risk_cache[ext] = (risk_level, content.capitalize())
            return risk_level, content.capitalize()

        except Exception as e:
            logger.error(f"⚠️ OpenAI analysis failed: {e}")
            return "suspicious", f"AI analysis failed: {str(e)}. Manual review recommended."
    else:
        # If OpenAI is not available, use extension-based heuristics
        if ext in ['.xml', '.json', '.html', '.css', '.log', '.ini', '.conf']:
            return "safe", "Text-based configuration file. Low security risk."
        else:
            return "suspicious", "Unknown file type. Manual review recommended."

def log_file_change(file_path, change_type):
    now = timezone.now()
    rounded_timestamp = now.replace(microsecond=0)

    dedup_string = f"{file_path}-{change_type}-{rounded_timestamp.isoformat()}"
    dedup_key = hashlib.md5(dedup_string.encode()).hexdigest()

    # Check if entry with this dedup_key already exists
    if FileChangeLog.objects.filter(dedup_key=dedup_key).exists():
        logger.info(f"⚠️ Skipped duplicate (dedup key): {dedup_key}")
        return

    # Get risk level and recommendation
    risk_level, recommendation = analyze_file_risk(file_path, change_type)

    # Create log entry
    FileChangeLog.objects.create(
        file_path=file_path,
        change_type=change_type,
        risk_level=risk_level,
        recommendation=recommendation,
        dedup_key=dedup_key
    )
    logger.info(f"✅ Logged event with dedup key: {dedup_key}")