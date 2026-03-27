# Make Celery app available as 'config.celery_app'
# This triggers autodiscovery on Django startup.
from .celery import app as celery_app  # noqa: F401

__all__ = ['celery_app']
