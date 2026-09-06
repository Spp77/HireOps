from django.db.models import Q, QuerySet
from .models import Job
from apps.accounts.models import User


def get_active_jobs() -> QuerySet[Job]:
    """Return all currently active jobs optimized with select_related."""
    return (
        Job.objects
        .filter(status=Job.Status.ACTIVE)
        .select_related('company')
    )


def get_similar_jobs(job: Job, limit: int = 5) -> QuerySet[Job]:
    """Return jobs similar to the given job based on type, level, or location."""
    return (
        Job.objects
        .filter(status=Job.Status.ACTIVE)
        .exclude(id=job.id)
        .filter(
            Q(job_type=job.job_type) |
            Q(experience_level=job.experience_level) |
            Q(location__icontains=job.location.split(',')[0])
        )
        .select_related('company')
        .distinct()[:limit]
    )


def get_jobs_for_recruiter(user: User) -> QuerySet[Job]:
    """Return all jobs posted by a specific recruiter's company."""
    return (
        Job.objects
        .filter(company__recruiter=user)
        .select_related('company')
    )