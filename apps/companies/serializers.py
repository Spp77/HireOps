from rest_framework import serializers
from .models import Company, CompanyFollow


class CompanySerializer(serializers.ModelSerializer):
    recruiter_email = serializers.EmailField(source='recruiter.email', read_only=True)
    followers_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'email', 'logo',
            'description', 'website', 'location',
            'industry', 'size',
            'recruiter_email', 'followers_count',
        ]
        read_only_fields = ['id', 'recruiter_email', 'followers_count']


class CompanyFollowSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = CompanyFollow
        fields = ['id', 'company', 'company_name', 'created_at']
        read_only_fields = ['id', 'company_name', 'created_at']
