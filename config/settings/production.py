"""
config/settings/production.py
──────────────────────────────────────────────────────────────────
Production-hardened overrides.
Set ENV=production on the server to activate.

All secrets MUST come from environment variables — never hardcoded.
"""

from .base import *       # noqa: F401, F403
from .base import MIDDLEWARE

# ─────────────────────────────────────────────────────────────────
# Core
# ─────────────────────────────────────────────────────────────────
DEBUG = False

# ─────────────────────────────────────────────────────────────────
# Security Headers  (OWASP hardened)
# ─────────────────────────────────────────────────────────────────

# Force HTTPS everywhere
SECURE_SSL_REDIRECT          = True
SECURE_PROXY_SSL_HEADER      = ('HTTP_X_FORWARDED_PROTO', 'https')

# HTTP Strict Transport Security — 1 year + subdomains
SECURE_HSTS_SECONDS          = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD          = True

# Cookie security
SESSION_COOKIE_SECURE        = True
SESSION_COOKIE_HTTPONLY      = True
SESSION_COOKIE_SAMESITE      = 'Lax'
CSRF_COOKIE_SECURE           = True
CSRF_COOKIE_HTTPONLY         = True
CSRF_COOKIE_SAMESITE         = 'Strict'

# Browser XSS / content-type sniffing hardening
SECURE_CONTENT_TYPE_NOSNIFF  = True
SECURE_BROWSER_XSS_FILTER    = True
X_FRAME_OPTIONS              = 'DENY'
SECURE_REFERRER_POLICY       = 'strict-origin-when-cross-origin'

# Permissions Policy (disable unused browser APIs)
PERMISSIONS_POLICY = {
    'camera':      [],
    'microphone':  [],
    'geolocation': [],
}

# ─────────────────────────────────────────────────────────────────
# Whitenoise  (serve static files directly from Gunicorn, no nginx needed)
# ─────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # must be 3rd
] + [m for m in MIDDLEWARE if m not in (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ─────────────────────────────────────────────────────────────────
# Swagger / ReDoc — disable in production (or gate behind admin check)
# ─────────────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    **globals().get('SPECTACULAR_SETTINGS', {}),
    'SERVE_INCLUDE_SCHEMA': False,
}

# ─────────────────────────────────────────────────────────────────
# Production Email  (SMTP)
# ─────────────────────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# ─────────────────────────────────────────────────────────────────
# Logging — write JSON to stdout (captured by log aggregators)
# ─────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {'()': 'apps.common.logging.JsonFormatter'},
    },
    'handlers': {
        'console': {
            'class':     'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level':    'WARNING',
    },
    'loggers': {
        'django.request': {
            'handlers':  ['console'],
            'level':     'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers':  ['console'],
            'level':     'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers':  ['console'],
            'level':     'WARNING',
            'propagate': False,
        },
    },
}

# ─────────────────────────────────────────────────────────────────
# File Uploads — limit upload size to prevent DoS
# ─────────────────────────────────────────────────────────────────
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024   # 5 MB form fields
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB file buffer
