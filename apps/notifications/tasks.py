"""
apps/accounts/tasks.py — already created above.
apps/notifications/tasks.py
─────────────────────────────────────────────────────────────────
Celery tasks for async notification delivery.
"""
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name='notifications.send_email_notification',
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 30},
)
def send_email_notification(self, recipient_id: int, subject: str, body: str):
    """
    Sends an email to a user asynchronously.
    Called by notify() when EMAIL_NOTIFICATIONS=True in env.
    """
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail
    from django.conf import settings

    User = get_user_model()
    try:
        user = User.objects.get(pkid=recipient_id)
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info('Email notification sent to %s: %s', user.email, subject)
    except User.DoesNotExist:
        logger.warning('send_email_notification: user %s not found', recipient_id)
