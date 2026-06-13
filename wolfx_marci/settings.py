"""
Django settings for wolfx_marci project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ──
SECRET_KEY  = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG       = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = ['*']

# ── Applications ──
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'django_api_helper',
    'rest_framework',
    'corsheaders',

    # Project apps
    'api',
    'config',
    'memory',
    'bus',
    'budget',
    'dashboard',
]

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

ROOT_URLCONF = 'wolfx_marci.urls'

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

WSGI_APPLICATION = 'wolfx_marci.wsgi.application'

# ── Database ──
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     os.getenv('DB_NAME',     'wolfx_marci'),
        'USER':     os.getenv('DB_USER',     'wolfx_marci_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST':     os.getenv('DB_HOST',     '127.0.0.1'),
        'PORT':     os.getenv('DB_PORT',     '5432'),
    }
}

# ── Auth ──
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ──
LANGUAGE_CODE    = 'en-us'
TIME_ZONE        = 'Asia/Kolkata'
USE_I18N         = True
USE_TZ           = True

# ── Static + Media ──
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── CORS ──
CORS_ALLOW_ALL_ORIGINS  = True
CORS_ALLOW_CREDENTIALS  = True

# ── REST Framework ──
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ── Celery ──
CELERY_BROKER_URL               = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND           = os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT           = ['json']
CELERY_TASK_SERIALIZER          = 'json'
CELERY_RESULT_SERIALIZER        = 'json'
CELERY_TIMEZONE                 = 'Asia/Kolkata'
CELERY_TASK_TRACK_STARTED       = True
CELERY_TASK_TIME_LIMIT          = 300       # 5 min hard limit
CELERY_TASK_SOFT_TIME_LIMIT     = 240       # 4 min soft limit
CELERY_WORKER_CONCURRENCY       = 2
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# ── Celery Beat ──
from celery.schedules import crontab

# CELERY_BEAT_SCHEDULE = {
#     'fire-scheduled-tasks': {
#         'task':     'bus.tasks.fire_scheduled_tasks',
#         'schedule': 60.0,                           # every 60 seconds
#     },
#     'summarise-sessions': {
#         'task':     'bus.tasks.summarise_sessions',
#         'schedule': crontab(minute=0),              # every hour
#     },
# }

# ── LLM ──
OPENAI_API_KEY          = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL_NANO       = os.getenv('OPENAI_MODEL_NANO',   'gpt-5-nano')       # DO NOT CHANGE
OPENAI_MODEL_DEFAULT    = os.getenv('OPENAI_MODEL_DEFAULT', 'gpt-5-nano')      # DO NOT CHANGE
OPENAI_EMBEDDING_MODEL  = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')

# ── Agent Mode ──
# mock  → zero API calls, static fixtures
# cheap → gpt-5-nano for everything, real calls
# full  → configured models per tool, real calls
AGENT_MODE = os.getenv('AGENT_MODE', 'mock')

# ── Tavily (web search) ──
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')

# ── Budget defaults ──
BUDGET_DEFAULT_DAILY_TOKEN_LIMIT    = int(os.getenv('BUDGET_DAILY_TOKEN_LIMIT',   '50000'))
BUDGET_DEFAULT_MONTHLY_TOKEN_LIMIT  = int(os.getenv('BUDGET_MONTHLY_TOKEN_LIMIT', '500000'))
BUDGET_ALERT_WEBHOOK                = os.getenv('BUDGET_ALERT_WEBHOOK', '')     # WhatsApp number to alert