from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedUUIDModel
from apps.jobs.models import Job


class Application(TimeStampedUUIDModel):

    class Status(models.TextChoices):
        PENDING    = "PENDING",    "Pending"
        REVIEWING  = "REVIEWING",  "Reviewing"
        SHORTLISTED = "SHORTLISTED", "Shortlisted"
        ACCEPTED   = "ACCEPTED",  "Accepted"
        REJECTED   = "REJECTED",  "Rejected"
        WITHDRAWN  = "WITHDRAWN", "Withdrawn"

    candidate    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    job          = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    resume       = models.FileField(upload_to='applications/resumes/', blank=True, null=True)
    status       = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    class Meta:
        unique_together = ('candidate', 'job')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.candidate.email} → {self.job.title}"


class SavedJob(TimeStampedUUIDModel):
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_jobs',
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')

    class Meta:
        unique_together = ('candidate', 'job')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.candidate.email} saved {self.job.title}"
