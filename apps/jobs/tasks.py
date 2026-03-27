"""
apps/jobs/tasks.py
─────────────────────────────────────────────────────────────────
Celery tasks for the jobs app.

These run asynchronously in worker processes, decoupled from the
HTTP request/response cycle.
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    name='jobs.close_expired_jobs',
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
)
def close_expired_jobs(self):
    """
    Periodic task (runs nightly via Celery Beat):
    Moves all ACTIVE jobs whose deadline has passed to CLOSED.
    """
    from .models import Job

    today = timezone.now().date()
    expired_qs = Job.objects.filter(
        status=Job.Status.ACTIVE,
        deadline__lt=today,
    )
    count = expired_qs.update(status=Job.Status.CLOSED)
    logger.info('Closed %d expired jobs', count)
    return {'closed': count}


@shared_task(
    name='jobs.sync_application_count',
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 10},
)
def sync_job_application_count(job_id: str):
    """
    Called after every application create/withdraw to keep the
    cached application_count on Job accurate.
    """
    from .models import Job
    from django.db.models import F

    try:
        job = Job.objects.get(id=job_id)
        count = job.applications.exclude(status='WITHDRAWN').count()
        Job.objects.filter(id=job_id).update(application_count=count)
        logger.debug('Synced application_count for job %s → %d', job_id, count)
    except Job.DoesNotExist:
        logger.warning('sync_job_application_count: job %s not found', job_id)
