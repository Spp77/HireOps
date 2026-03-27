from rest_framework import serializers
from .models import Application, SavedJob
from apps.jobs.serializers import JobSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    """Write serializer used when a candidate submits an application."""
    candidate_email = serializers.EmailField(source='candidate.email', read_only=True)
    job_title       = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'candidate_email', 'job', 'job_title',
            'cover_letter', 'resume', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'candidate_email', 'job_title', 'status', 'created_at']


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """Rich read serializer used in list views — includes nested job details."""

    class CandidateSummary(serializers.Serializer):
        id         = serializers.UUIDField()
        email      = serializers.EmailField()
        first_name = serializers.CharField()
        last_name  = serializers.CharField()

    candidate = CandidateSummary(read_only=True)
    job       = JobSerializer(read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'candidate', 'job',
            'cover_letter', 'resume', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status']


class SavedJobSerializer(serializers.ModelSerializer):
    job_title    = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.name', read_only=True)

    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'job_title', 'company_name', 'created_at']
        read_only_fields = ['id', 'job_title', 'company_name', 'created_at']
