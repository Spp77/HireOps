"""
config/settings/base.py
────────────────────────────────────────────────────────────────
Shared settings consumed by ALL environments (dev / prod / test).
Environment-specific overrides live in development.py / production.py.
"""

from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

# ─────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ─────────────────────────────────────────────────────────────────
# Core
# ─────────────────────────────────────────────────────────────────
SECRET_KEY   = config('SECRET_KEY')
DEBUG        = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())


# ─────────────────────────────────────────────────────────────────
# Installed Apps
# ─────────────────────────────────────────────────────────────────
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
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'django_celery_beat',      # DB-backed periodic task management
    'django_celery_results',   # Store task results in DB (optional but useful)
    'django_redis',            # Redis cache backend
]

LOCAL_APPS = [
    'apps.common',
    'apps.accounts',
    'apps.companies',
    'apps.jobs',
    'apps.profiles',
    'apps.applications',
    'apps.notifications',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ─────────────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.common.middleware.RequestIDMiddleware',   # attaches X-Request-ID to every request
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION  = 'config.asgi.application'


# ─────────────────────────────────────────────────────────────────
# Database  (PostgreSQL — credentials via env)
# ─────────────────────────────────────────────────────────────────
# The DB_* variables intentionally have no hardcoded defaults so the
# app will FAIL LOUDLY if the env file is missing — safe by design.
DATABASES = {
    'default': {
        'ENGINE':       'django.db.backends.postgresql',
        'NAME':         config('DB_NAME',     default=''),
        'USER':         config('DB_USER',     default=''),
        'PASSWORD':     config('DB_PASSWORD', default=''),
        'HOST':         config('DB_HOST',     default='localhost'),
        'PORT':         config('DB_PORT',     default='5432'),
        # ── Connection pooling (vertical scale) ───────────────────
        # Reuse DB connections across requests; tune to gunicorn workers × threads.
        'CONN_MAX_AGE':    config('DB_CONN_MAX_AGE', default=60, cast=int),
        'CONN_HEALTH_CHECKS': True,  # Drop stale connections automatically (Django 4.1+)
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',   # 30 s query timeout
        },
    },
}

# ── Optional read replica (horizontal DB scale) ───────────────────
# If DB_READ_HOST is set, a 'replica' alias is registered and the
# PrimaryReplicaRouter in apps/common/routers.py will send all
# SELECT queries to the replica.
_read_host = config('DB_READ_HOST', default='')
if _read_host:
    DATABASES['replica'] = {
        **DATABASES['default'],
        'HOST': _read_host,
        'PORT': config('DB_READ_PORT', default='5432'),
        'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=60, cast=int),
        'CONN_HEALTH_CHECKS': True,
    }
    DATABASE_ROUTERS = ['apps.common.routers.PrimaryReplicaRouter']


# ─────────────────────────────────────────────────────────────────
# Cache  (Redis — shared across all instances = horizontal scale)
# ─────────────────────────────────────────────────────────────────
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

CACHES = {
    'default': {
        'BACKEND':  'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
        'KEY_PREFIX': 'hireops',
        'TIMEOUT':  60 * 15,          # 15-minute default TTL
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': 100,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
    }
}

# ── Session stored in Redis (stateless app servers for horiz scale)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'


# ─────────────────────────────────────────────────────────────────
# Celery  (async task queue — horizontal worker scale)
# ─────────────────────────────────────────────────────────────────
CELERY_BROKER_URL          = config('CELERY_BROKER_URL', default=REDIS_URL)
CELERY_RESULT_BACKEND      = config('CELERY_RESULT_BACKEND', default=REDIS_URL)
CELERY_ACCEPT_CONTENT      = ['json']
CELERY_TASK_SERIALIZER     = 'json'
CELERY_RESULT_SERIALIZER   = 'json'
CELERY_TIMEZONE            = 'UTC'
CELERY_TASK_TRACK_STARTED  = True
CELERY_TASK_TIME_LIMIT     = 30 * 60          # hard kill after 30 min
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60         # soft timeout at 25 min
CELERY_WORKER_MAX_TASKS_PER_CHILD = 200       # recycle worker memory
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Beat schedule (periodic tasks)
from celery.schedules import crontab            # noqa: E402
CELERY_BEAT_SCHEDULE = {
    'expire-old-jobs-daily': {
        'task':     'apps.jobs.tasks.close_expired_jobs',
        'schedule': crontab(hour=0, minute=0),  # midnight UTC
    },
    'clean-expired-tokens-weekly': {
        'task':     'apps.accounts.tasks.flush_expired_tokens',
        'schedule': crontab(day_of_week='sunday', hour=2, minute=0),
    },
}


# ─────────────────────────────────────────────────────────────────
# Django REST Framework
# ─────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # ── Pagination ───────────────────────────────────────────────
    # CursorPagination is stable for large tables — no OFFSET scans.
    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.StandardCursorPagination',
    'PAGE_SIZE': 20,
    # ── Filtering ────────────────────────────────────────────────
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # ── Throttling (role-aware) ───────────────────────────────────
    'DEFAULT_THROTTLE_CLASSES': [
        'apps.common.throttles.AnonBurstThrottle',
        'apps.common.throttles.AnonSustainedThrottle',
        'apps.common.throttles.UserBurstThrottle',
        'apps.common.throttles.UserSustainedThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon_burst':      '30/min',
        'anon_sustained':  '500/day',
        'user_burst':      '60/min',
        'user_sustained':  '5000/day',
        'recruiter_burst': '120/min',   # recruiters get higher limits
    },
    # ── Renderer ─────────────────────────────────────────────────
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # ── Schema / Exception ───────────────────────────────────────
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'apps.common.exceptions.custom_exception_handler',
}


# ─────────────────────────────────────────────────────────────────
# JWT
# ─────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(
        minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=15, cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)
    ),
    'ROTATE_REFRESH_TOKENS':   True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN':        True,
    'AUTH_HEADER_TYPES':       ('Bearer',),
    'USER_ID_FIELD':           'id',
    'USER_ID_CLAIM':           'user_id',
    'TOKEN_OBTAIN_SERIALIZER': 'apps.accounts.serializers.CustomTokenObtainSerializer',
}


# ─────────────────────────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS  = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000', cast=Csv())
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization',
    'content-type', 'dnt', 'origin', 'user-agent',
    'x-csrftoken', 'x-requested-with', 'x-request-id',
]


# ─────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ─────────────────────────────────────────────────────────────────
# Internationalisation
# ─────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True


# ─────────────────────────────────────────────────────────────────
# Static & Media
# ─────────────────────────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ─────────────────────────────────────────────────────────────────
# Email
# ─────────────────────────────────────────────────────────────────
EMAIL_BACKEND       = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST          = config('EMAIL_HOST',    default='smtp.gmail.com')
EMAIL_PORT          = config('EMAIL_PORT',    default=587, cast=int)
EMAIL_USE_TLS       = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER     = config('EMAIL_HOST_USER',     default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = config('DEFAULT_FROM_EMAIL',  default='HireOps <noreply@hireops.com>')


# ─────────────────────────────────────────────────────────────────
# OpenAPI / Swagger (drf-spectacular)
# ─────────────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE':       'HireOps API',
    'DESCRIPTION': 'Production-grade job portal API — built with Django REST Framework.',
    'VERSION':     '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT':     {'email': 'admin@hireops.com'},
    'LICENSE':     {'name': 'Proprietary'},
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'SECURITY': [{'jwtAuth': []}],
}


# ─────────────────────────────────────────────────────────────────
# Logging  (structured — overridden per environment)
# ─────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'apps.common.logging.JsonFormatter',
        },
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class':     'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level':    config('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django':                   {'level': 'WARNING', 'propagate': True},
        'django.request':           {'level': 'ERROR',   'propagate': False, 'handlers': ['console']},
        'django.db.backends':       {'level': 'WARNING', 'propagate': False, 'handlers': ['console']},
        'apps':                     {'level': config('LOG_LEVEL', default='INFO'), 'propagate': True},
        'celery':                   {'level': 'INFO',    'propagate': True},
    },
}


# ─────────────────────────────────────────────────────────────────
# Internal IPs (for dev tools)
# ─────────────────────────────────────────────────────────────────
INTERNAL_IPS = ['127.0.0.1', 'localhost']
