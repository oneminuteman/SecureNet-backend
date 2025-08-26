"""
Django settings for securanet_backend project.
Merged to support:
 - securanet (original app)
 - phishing_email
 - phishing_detection
 - file monitoring configuration
Includes DRF, CORS, drf_yasg, Channels (optional via Redis), and dev media.
"""

from pathlib import Path
from decouple import config, Csv
import os
import json

# -----------------------------------------------------------------------------
# Base paths
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Security / Debug
# -----------------------------------------------------------------------------
# Prefer .env values; provide sane dev defaults
SECRET_KEY = config(
    "DJANGO_SECRET_KEY",
    default="django-insecure-CHANGE-ME"
)

DEBUG = config("DEBUG", default=True, cast=bool)

# Accept a CSV list from env; fall back to localhost if not set
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1,[::1]", cast=Csv())

# -----------------------------------------------------------------------------
# CSRF / Cookies
# -----------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"
# NOTE: set both to True in production behind HTTPS
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=False, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=False, cast=bool)

# -----------------------------------------------------------------------------
# Applications
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "corsheaders",
    "drf_yasg",

    # Local apps
    "securanet",              # original app
    "phishing_email",         # new app
    "phishing_detection",     # new app
    # If you also have a separate file management app, add it here:
     "file_management",
]

# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # keep first for CORS
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -----------------------------------------------------------------------------
# URL / WSGI / ASGI
# -----------------------------------------------------------------------------
ROOT_URLCONF = "securanet_backend.urls"
WSGI_APPLICATION = "securanet_backend.wsgi.application"

# If you have Channels routing (and channels installed), enable this:
ASGI_APPLICATION = config(
    "ASGI_APPLICATION",
    default="securanet_backend.routing.application"
)

# Optional Channels + Redis (only used if you install/configure Redis)
# You can disable by setting USE_CHANNELS=false in your .env
USE_CHANNELS = config("USE_CHANNELS", default=False, cast=bool)
if USE_CHANNELS:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [(config("REDIS_HOST", default="127.0.0.1"), config("REDIS_PORT", default=6379, cast=int))]},
        },
    }

# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -----------------------------------------------------------------------------
# Password validation
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Static & Media
# -----------------------------------------------------------------------------
STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "securanet_backend", "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------------------------------
# CORS
# -----------------------------------------------------------------------------
# Allow explicit origins by default; you can override with CORS_ALLOW_ALL_ORIGINS=true
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default=False, cast=bool)

# -----------------------------------------------------------------------------
# Third-party API Keys
# -----------------------------------------------------------------------------
OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
VT_API_KEY = config("VT_API_KEY", default="")
GOOGLE_SAFE_BROWSING_API_KEY = config("GOOGLE_SAFE_BROWSING_API_KEY", default="")
WHOISXML_API_KEY = config("WHOISXML_API_KEY", default="")

# -----------------------------------------------------------------------------
# File Monitoring Settings
# (preserved and made configurable via env or monitor_config.json)
# -----------------------------------------------------------------------------
CONFIG_FILE = os.path.join(BASE_DIR, "monitor_config.json")

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            MONITOR_CONFIG = json.load(f)
    except Exception:
        MONITOR_CONFIG = {"mode": "custom", "paths": [], "excludes": []}
else:
    # Defaults if no file is present
    MONITOR_CONFIG = {
        "mode": "custom",
        "paths": [os.path.expanduser("~/Documents")],
        "excludes": [
            "C:/Windows",
            "C:/Program Files",
            "C:/Program Files (x86)",
        ],
    }

WATCH_FOLDER = os.environ.get(
    "WATCH_FOLDER",
    MONITOR_CONFIG["paths"][0] if MONITOR_CONFIG.get("paths") else os.path.expanduser("~/Documents"),
)

DEDUP_WINDOW_SECONDS = config("DEDUP_WINDOW_SECONDS", default=5, cast=int)
IGNORE_TEMP_FILES = config("IGNORE_TEMP_FILES", default=True, cast=bool)
IGNORE_DIRECTORIES = config("IGNORE_DIRECTORIES", default=True, cast=bool)
