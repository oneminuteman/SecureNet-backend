import os
import json
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv
import environ

# === Env Setup ===
env = environ.Env()
environ.Env.read_env()

# === Base Directory ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Security Settings ===
SECRET_KEY = config('SECRET_KEY', default='django-insecure-placeholder')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default="localhost,127.0.0.1")

# === CSRF & Session Settings ===
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000"
]
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)

SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)

# === CORS Settings ===
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]

# === Application Definition ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'channels',
    'securanet',           # Replace with actual app name
    'myapp',
    'myapp.file_monitor',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ✅ First
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === URL & WSGI/ASGI ===
ROOT_URLCONF = 'securanet_backend.urls'
WSGI_APPLICATION = 'securanet_backend.wsgi.application'
ASGI_APPLICATION = 'securanet_backend.routing.application'

# === Templates ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# === Database (SQLite) ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# === Password Validation ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === Internationalization ===
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# === Static & Media ===
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'securanet_backend', 'media')

# === Default Auto Field ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === API Keys ===
VT_API_KEY = os.getenv("VT_API_KEY", "")
GOOGLE_SAFE_BROWSING_API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "")
WHOISXML_API_KEY = os.getenv("WHOISXML_API_KEY", "")
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')

# === Channels Layer (Redis) ===
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# === File Monitor Config ===
CONFIG_FILE = os.path.join(BASE_DIR, 'monitor_config.json')
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        MONITOR_CONFIG = json.load(f)
else:
    MONITOR_CONFIG = {
        'mode': 'custom',
        'paths': [os.path.expanduser('~/Documents')],
        'excludes': [
            'C:/Windows',
            'C:/Program Files',
            'C:/Program Files (x86)'
        ]
    }

WATCH_FOLDER = os.environ.get(
    'WATCH_FOLDER',
    MONITOR_CONFIG['paths'][0] if MONITOR_CONFIG['paths'] else os.path.expanduser('~/Documents')
)

DEDUP_WINDOW_SECONDS = config('DEDUP_WINDOW_SECONDS', default=5, cast=int)
IGNORE_TEMP_FILES = config('IGNORE_TEMP_FILES', default=True, cast=bool)
IGNORE_DIRECTORIES = config('IGNORE_DIRECTORIES', default=True, cast=bool)

