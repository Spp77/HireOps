from rest_framework import serializers
from .models import CandidateProfile, WorkExperience, Education


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = [
            'id', 'company_name', 'title', 'location',
            'start_date', 'end_date', 'is_current', 'description',
        ]
        read_only_fields = ['id']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            'id', 'institution', 'degree', 'field_of_study',
            'start_date', 'end_date', 'is_current', 'grade',
        ]
        read_only_fields = ['id']


class CandidateProfileSerializer(serializers.ModelSerializer):
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    education        = EducationSerializer(many=True, read_only=True)
    completeness     = serializers.IntegerField(read_only=True)
    user_email       = serializers.EmailField(source='user.email', read_only=True)
    full_name        = serializers.SerializerMethodField()

    class Meta:
        model = CandidateProfile
        fields = [
            'id', 'user_email', 'full_name', 'headline', 'bio', 'phone',
            'location', 'experience_years', 'skills',
            'resume', 'linkedin_url', 'portfolio_url', 'github_url',
            'availability', 'desired_salary',
            'completeness', 'work_experiences', 'education',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user_email', 'full_name', 'completeness', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name()
