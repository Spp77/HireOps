from rest_framework import serializers
from .models import Job
from apps.companies.serializers import CompanySerializer


class JobSerializer(serializers.ModelSerializer):
    """Full read serializer — includes nested company and analytics."""
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'location',
            'job_type', 'experience_level', 'skills_required',
            'salary_min', 'salary_max',
            'description', 'requirements',
            'status', 'deadline',
            'view_count', 'application_count',
            'created_at',
        ]


class JobWriteSerializer(serializers.ModelSerializer):
    """Write serializer for create / update."""
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'location',
            'job_type', 'experience_level', 'skills_required',
            'salary_min', 'salary_max',
            'description', 'requirements',
            'status', 'deadline',
        ]

    def validate(self, attrs):
        salary_min = attrs.get('salary_min')
        salary_max = attrs.get('salary_max')
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError("salary_min cannot be greater than salary_max.")
        return attrs


class JobMiniSerializer(serializers.ModelSerializer):
    """Compact serializer for related job lists (e.g. similar jobs, recruiter dashboard)."""
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company_name', 'location',
            'job_type', 'experience_level',
            'salary_min', 'salary_max',
            'status', 'deadline',
            'view_count', 'application_count',
            'created_at',
        ]