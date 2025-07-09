
# securanet_backend/settings.py

import os
from pathlib import Path

# === VirusTotal API Key ===
VT_API_KEY = os.getenv("VT_API_KEY", "")  # ✅ You can set this in .env or your OS env variables

# === Base Directory ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Security Settings ===
SECRET_KEY = 'django-insecure-dj(dw#z+go3mgp*4&(0ztb!66f60x-%u2j&ot0%h3nrbmf^b8+'
DEBUG = True
ALLOWED_HOSTS = []

# === Installed Apps ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',     # ✅ For frontend-backend connection
    'securanet',        # ✅ Your main app
]

# === Middleware ===
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === CORS Settings ===
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # ✅ Frontend (Vite) URL
]

# === URL Configuration ===
ROOT_URLCONF = 'securanet_backend.urls'

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

# === WSGI ===
WSGI_APPLICATION = 'securanet_backend.wsgi.application'

# === Database ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# === Password Validators ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === Localization ===
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# === Static Files ===
STATIC_URL = '/static/'

# === Media Files (for screenshots, etc.) ===
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# === Auto Field Default ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
