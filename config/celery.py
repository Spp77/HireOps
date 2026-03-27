"""
config/celery.py
─────────────────────────────────────────────────────────────────
Celery application factory.

Workers are started separately from the Django process and can
be scaled horizontally on any number of machines:

  # Start worker (production)
  celery -A config worker --loglevel=info --concurrency=8

  # Start beat scheduler (1 instance only)
  celery -A config beat  --loglevel=info

  # Monitor with Flower (optional)
  celery -A config flower
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('hireops')

# Read all CELERY_* settings from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in every INSTALLED_APP
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Ping task — useful for smoke-testing worker connectivity."""
    print(f'Request: {self.request!r}')
