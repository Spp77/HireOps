import django_filters
from .models import Job


class JobFilter(django_filters.FilterSet):
    location        = django_filters.CharFilter(lookup_expr='icontains')
    job_type        = django_filters.ChoiceFilter(choices=Job.JobType.choices)
    experience_level = django_filters.ChoiceFilter(choices=Job.ExperienceLevel.choices)
    salary_min      = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_max      = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    company         = django_filters.UUIDFilter(field_name='company__id')

    class Meta:
        model = Job
        fields = ['location', 'job_type', 'experience_level', 'salary_min', 'salary_max', 'company']
