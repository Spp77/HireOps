from django.db import models
from apps.common.models import TimeStampedUUIDModel
from apps.companies.models import Company


class Job(TimeStampedUUIDModel):

    class Status(models.TextChoices):
        ACTIVE  = "ACTIVE",  "Active"
        CLOSED  = "CLOSED",  "Closed"
        DRAFT   = "DRAFT",   "Draft"

    class JobType(models.TextChoices):
        FULL_TIME  = "FULL_TIME",  "Full Time"
        PART_TIME  = "PART_TIME",  "Part Time"
        CONTRACT   = "CONTRACT",   "Contract"
        INTERNSHIP = "INTERNSHIP", "Internship"
        REMOTE     = "REMOTE",     "Remote"

    class ExperienceLevel(models.TextChoices):
        ENTRY  = "ENTRY",  "Entry Level"
        MID    = "MID",    "Mid Level"
        SENIOR = "SENIOR", "Senior Level"
        LEAD   = "LEAD",   "Lead / Manager"

    title            = models.CharField(max_length=255)
    company          = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    location         = models.CharField(max_length=255)
    description      = models.TextField()
    requirements     = models.TextField()
    salary_min       = models.PositiveIntegerField(null=True, blank=True)
    salary_max       = models.PositiveIntegerField(null=True, blank=True)
    job_type         = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME, db_index=True)
    experience_level = models.CharField(max_length=20, choices=ExperienceLevel.choices, default=ExperienceLevel.MID, db_index=True)
    skills_required  = models.JSONField(default=list, blank=True)
    status           = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    deadline         = models.DateField(null=True, blank=True)

    # ── Analytics ──────────────────────────────────────────────
    view_count        = models.PositiveIntegerField(default=0, editable=False)
    application_count = models.PositiveIntegerField(default=0, editable=False)

    def __str__(self):
        return f"{self.title} @ {self.company.name}"

    def increment_views(self):
        """Atomically increment the view counter."""
        Job.objects.filter(pk=self.pk).update(view_count=models.F('view_count') + 1)

    def sync_application_count(self):
        """Sync cached application_count from real data (call post-application actions)."""
        count = self.applications.exclude(status='WITHDRAWN').count()
        Job.objects.filter(pk=self.pk).update(application_count=count)