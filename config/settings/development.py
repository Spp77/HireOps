"""
config/settings/development.py
──────────────────────────────────────────────────────────────────
Local development overrides.
Set ENV=development (default) to activate.
"""

from .base import *       # noqa: F401, F403
from .base import INSTALLED_APPS, MIDDLEWARE, CACHES, REST_FRAMEWORK

# ── Dev-mode flags ────────────────────────────────────────────────
DEBUG = True

# ── Relaxed throttling so local testing is easy ──────────────────
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon_burst':      '200/min',
    'anon_sustained':  '10000/day',
    'user_burst':      '600/min',
    'user_sustained':  '50000/day',
    'recruiter_burst': '600/min',
}

# ── Use console email in dev ──────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ── Fallback to in-memory cache if Redis not running locally ──────
# Comment out to use Redis locally too.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'hireops-dev',
    }
}

# ── Show SQL in console (set LOG_LEVEL=DEBUG in .env to enable) ───
import logging
if logging.getLogger().level <= logging.DEBUG:
    import django.db
    django.db.backends.base.schema   # noqa — lazy import to not break startup

# ── CORS: allow all origins in dev ───────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ── Disable HTTPS requirements locally ───────────────────────────
SECURE_SSL_REDIRECT          = False
SESSION_COOKIE_SECURE        = False
CSRF_COOKIE_SECURE           = False
SECURE_HSTS_SECONDS          = 0

# ── Django Browsable API available in dev ─────────────────────────
REST_FRAMEWORK.setdefault('DEFAULT_RENDERER_CLASSES', []).append(
    'rest_framework.renderers.BrowsableAPIRenderer'
)
