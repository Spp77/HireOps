from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import CandidateProfile, WorkExperience, Education
from .serializers import (
    CandidateProfileSerializer,
    WorkExperienceSerializer,
    EducationSerializer,
)
from apps.common.exceptions import error_response
from apps.common.error_codes import ErrorCode


# ─────────────────────────────────────────────────────────────────
# Candidate Profile
# ─────────────────────────────────────────────────────────────────

class MyProfileView(generics.RetrieveUpdateAPIView):
    """Authenticated user views/edits their own profile."""
    serializer_class = CandidateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        try:
            kwargs['partial'] = True
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return error_response(ErrorCode.PROFILE_UPDATE_FAILED, str(e))


# ─────────────────────────────────────────────────────────────────
# Work Experience Sub-resource
# ─────────────────────────────────────────────────────────────────

class WorkExperienceListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        return WorkExperience.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        serializer.save(profile=profile)


class WorkExperienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        return WorkExperience.objects.filter(profile=profile)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────────
# Education Sub-resource
# ─────────────────────────────────────────────────────────────────

class EducationListCreateView(generics.ListCreateAPIView):
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        return Education.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        serializer.save(profile=profile)


class EducationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        return Education.objects.filter(profile=profile)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
