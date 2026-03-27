"""
apps/accounts/tasks.py
─────────────────────────────────────────────────────────────────
Celery tasks for the accounts app.
"""
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name='accounts.flush_expired_tokens')
def flush_expired_tokens():
    """
    Periodic task (runs weekly via Celery Beat):
    Removes expired JWT tokens from the blacklist to keep the table small.
    Django SimpleJWT provides this utility through the token_blacklist app.
    """
    try:
        from django.utils import timezone
        from rest_framework_simplejwt.token_blacklist.models import (
            OutstandingToken,
            BlacklistedToken,
        )

        # Delete outstanding tokens that have expired
        deleted, _ = OutstandingToken.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        logger.info('Flushed %d expired JWT outstanding tokens', deleted)
        return {'deleted': deleted}
    except Exception as exc:
        logger.error('flush_expired_tokens failed: %s', exc)
        raise


@shared_task(name='accounts.send_welcome_email', bind=True, max_retries=3)
def send_welcome_email(self, user_id: int):
    """
    Sends a welcome email to newly registered users.
    Runs asynchronously so registration response is instant.
    """
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail
    from django.conf import settings

    User = get_user_model()
    try:
        user = User.objects.get(pkid=user_id)
        send_mail(
            subject='Welcome to HireOps!',
            message=(
                f'Hi {user.first_name or user.username},\n\n'
                'Welcome to HireOps — the smart way to find great jobs.\n\n'
                'Complete your profile to get noticed by top recruiters.\n\n'
                '— The HireOps Team'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info('Welcome email sent to %s', user.email)
    except User.DoesNotExist:
        logger.warning('send_welcome_email: user %s not found', user_id)
    except Exception as exc:
        logger.error('send_welcome_email failed for user %s: %s', user_id, exc)
        raise self.retry(exc=exc, countdown=60)
