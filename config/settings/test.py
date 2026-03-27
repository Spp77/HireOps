"""
config/settings/test.py
─────────────────────────────────────────────────────────────────
Test environment — fast, isolated, no external services.
"""
from .base import *       # noqa: F401, F403

DEBUG = False
SECRET_KEY = 'test-secret-key-not-for-production'

# In-memory SQLite — fast, no PostgreSQL needed for CI
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# No cache I/O during tests
CACHES = {
    'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
}

# Silence all emails
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Instant (not async) task execution during tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Speed up password hashing
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
