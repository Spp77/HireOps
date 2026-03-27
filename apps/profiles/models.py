from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedUUIDModel


class CandidateProfile(TimeStampedUUIDModel):
    user             = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    bio              = models.TextField(blank=True)
    phone            = models.CharField(max_length=20, blank=True)
    location         = models.CharField(max_length=255, blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    skills           = models.JSONField(default=list, blank=True)
    resume           = models.FileField(upload_to='resumes/', blank=True, null=True)
    linkedin_url     = models.URLField(blank=True)
    portfolio_url    = models.URLField(blank=True)
    github_url       = models.URLField(blank=True)
    availability     = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g. Immediately, 2 weeks notice, Not looking",
    )
    desired_salary   = models.PositiveIntegerField(null=True, blank=True)
    headline         = models.CharField(max_length=255, blank=True, help_text="Short professional headline")

    def __str__(self):
        return f"{self.user.email} — profile"

    @property
    def completeness(self) -> int:
        """Return profile completeness percentage (0-100)."""
        scored_fields = {
            'bio':              bool(self.bio),
            'phone':            bool(self.phone),
            'location':         bool(self.location),
            'skills':           bool(self.skills),
            'resume':           bool(self.resume),
            'linkedin_url':     bool(self.linkedin_url),
            'headline':         bool(self.headline),
            'experience_years': self.experience_years > 0,
            'availability':     bool(self.availability),
            'desired_salary':   self.desired_salary is not None,
        }
        completed = sum(scored_fields.values())
        return int((completed / len(scored_fields)) * 100)


class WorkExperience(TimeStampedUUIDModel):
    profile      = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='work_experiences')
    company_name = models.CharField(max_length=255)
    title        = models.CharField(max_length=255)
    location     = models.CharField(max_length=255, blank=True)
    start_date   = models.DateField()
    end_date     = models.DateField(null=True, blank=True)
    is_current   = models.BooleanField(default=False)
    description  = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} @ {self.company_name}"


class Education(TimeStampedUUIDModel):
    profile      = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='education')
    institution  = models.CharField(max_length=255)
    degree       = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, blank=True)
    start_date   = models.DateField()
    end_date     = models.DateField(null=True, blank=True)
    is_current   = models.BooleanField(default=False)
    grade        = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.degree} — {self.institution}"
