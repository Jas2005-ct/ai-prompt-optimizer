"""
Base Django settings for AI Prompt Optimizer.
All environment-specific settings inherit from this.
"""
import os
from pathlib import Path
import environ

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=('localhost', '127.0.0.1'),
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Security
SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-change-me-in-production')
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'django_extensions',
]

LOCAL_APPS = [
    'apps.shared',
    'apps.ai_providers',
    'apps.prompt_templates',
    'apps.prompt_optimizer',
    'apps.analytics',
    'apps.dashboard',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR}/db.sqlite3')
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

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'apps.shared.exceptions.custom_exception_handler',
}

# AI Providers Configuration
AI_PROVIDERS = {
    'openai': {
        'api_key': env('OPENAI_API_KEY', default=''),
        'default_model': 'gpt-4o',
        'timeout': 30,
        'max_retries': 3,
    },
    'anthropic': {
        'api_key': env('ANTHROPIC_API_KEY', default=''),
        'default_model': 'claude-3-5-sonnet-20241022',
        'timeout': 30,
        'max_retries': 3,
    },
    'gemini': {
        'api_key': env('GEMINI_API_KEY', default=''),
        'default_model': 'gemini-1.5-pro',
        'timeout': 30,
        'max_retries': 3,
    },
    'groq': {
        'api_key': env('GROQ_API_KEY', default=''),
        'default_model': 'llama3-8b-8192',
        'timeout': 20,
        'max_retries': 3,
    },
    'deepseek': {
        'api_key': env('DEEPSEEK_API_KEY', default=''),
        'default_model': 'deepseek-chat',
        'timeout': 30,
        'max_retries': 3,
    },
    'openrouter': {
        'api_key': env('OPENROUTER_API_KEY', default=''),
        'default_model': 'openai/gpt-4o',
        'timeout': 30,
        'max_retries': 3,
    },
}

DEFAULT_AI_PROVIDER = env('DEFAULT_AI_PROVIDER', default='openrouter')
DEFAULT_AI_MODEL = env('DEFAULT_AI_MODEL', default='openai/gpt-oss-120b:free')

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ai-prompt-optimizer',
    }
}
