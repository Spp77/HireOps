from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedUUIDModel


class Company(TimeStampedUUIDModel):
    name        = models.CharField(max_length=255, unique=True)
    email       = models.EmailField()
    logo        = models.ImageField(upload_to="companies/logos/", default="default_company.png")
    description = models.TextField()
    website     = models.URLField()
    location    = models.CharField(max_length=255)
    industry    = models.CharField(max_length=100, blank=True)
    size        = models.CharField(max_length=50, blank=True, help_text="e.g. 1-10, 50-200, 1000+")

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="companies",
    )

    def __str__(self):
        return self.name

    @property
    def followers_count(self):
        return self.followers.count()


class CompanyFollow(TimeStampedUUIDModel):
    """Candidate follows a company to receive new-job notifications."""
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followed_companies",
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="followers")

    class Meta:
        unique_together = ('candidate', 'company')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.candidate.email} follows {self.company.name}"