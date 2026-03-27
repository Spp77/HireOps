from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedUUIDModel


class Notification(TimeStampedUUIDModel):
    class Type(models.TextChoices):
        APPLICATION_RECEIVED  = "APPLICATION_RECEIVED",  "Application Received"
        STATUS_CHANGED        = "STATUS_CHANGED",        "Application Status Changed"
        JOB_RECOMMENDED       = "JOB_RECOMMENDED",       "Job Recommended"
        COMPANY_NEW_JOB       = "COMPANY_NEW_JOB",       "New Job from Followed Company"
        GENERAL               = "GENERAL",               "General"

    recipient   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(
        max_length=30, choices=Type.choices, default=Type.GENERAL
    )
    title   = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)

    # Optional generic link context
    link = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.notification_type}] → {self.recipient.email}"
