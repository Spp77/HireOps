"""
Notification service — single entry-point to create in-app notifications.

Usage:
    from apps.notifications.services import notify

    notify(
        recipient=user,
        notification_type=Notification.Type.STATUS_CHANGED,
        title="Your application was reviewed",
        message="The recruiter has moved your application to 'Shortlisted'.",
        link=f"/applications/{application.id}/",
    )
"""
from .models import Notification


def notify(recipient, notification_type: str, title: str, message: str, link: str = "") -> Notification:
    """Create and persist an in-app notification for a user."""
    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
    )
