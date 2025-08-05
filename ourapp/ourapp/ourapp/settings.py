"""
Django settings for ourapp project.
"""
import os
from pathlib import Path
from decouple import config, Csv
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = config('SECRET_KEY', default='django-insecure-&bp4dlyzt6+)27qy-0)pf2_nmbfsjjj$z+4stvm9%i-j$6b0-t')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'myapp',
    'securanet',  # Clone detection app
    'corsheaders',
    'myapp.file_monitor'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ourapp.urls'

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

WSGI_APPLICATION = 'ourapp.wsgi.application'
ASGI_APPLICATION = 'ourapp.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (Uploads, Screenshots)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# API keys for clone detection services
GOOGLE_SAFE_BROWSING_API_KEY = config('GOOGLE_SAFE_BROWSING_API_KEY', default='')
VT_API_KEY = config('VT_API_KEY', default='')
WHOISXML_API_KEY = config('WHOISXML_API_KEY', default='')

# OpenAI settings
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Load monitor configuration
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

# Set watch folder from config (use first path or default)
WATCH_FOLDER = os.environ.get(
    'WATCH_FOLDER',
    MONITOR_CONFIG['paths'][0] if MONITOR_CONFIG['paths'] else os.path.expanduser('~/Documents')
)

# File monitor settings
DEDUP_WINDOW_SECONDS = config('DEDUP_WINDOW_SECONDS', default=5, cast=int)
IGNORE_TEMP_FILES = config('IGNORE_TEMP_FILES', default=True, cast=bool)
IGNORE_DIRECTORIES = config('IGNORE_DIRECTORIES', default=True, cast=bool)