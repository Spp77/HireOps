from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import Job
from .serializers import JobSerializer, JobWriteSerializer, JobMiniSerializer
from .filters import JobFilter
from apps.accounts.models import User
from apps.common.exceptions import error_response
from apps.common.error_codes import ErrorCode


# ─────────────────────────────────────────────────────────────────
# Permissions
# ─────────────────────────────────────────────────────────────────

class IsRecruiterOwner(permissions.BasePermission):
    """Allow mutations only for the recruiter who owns the job's company."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.company.recruiter == request.user


# ─────────────────────────────────────────────────────────────────
# Public / Candidate Job Browsing
# ─────────────────────────────────────────────────────────────────

class JobListAPIView(generics.ListAPIView):
    """Public endpoint: search, filter and browse active jobs."""
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]
    filterset_class = JobFilter
    search_fields = ['title', 'company__name', 'description', 'location', 'skills_required']
    ordering_fields = ['created_at', 'title', 'salary_min', 'view_count', 'application_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Job.objects
            .filter(status=Job.Status.ACTIVE)
            .select_related('company')
        )


class JobDetailAPIView(generics.RetrieveAPIView):
    """Public endpoint: view job details + increment view counter."""
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Job.objects.select_related('company').all()
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def similar_jobs(request, id):
    """Return up to 5 jobs similar to the given job (same type/level/location)."""
    try:
        job = Job.objects.select_related('company').get(id=id, status=Job.Status.ACTIVE)
    except Job.DoesNotExist:
        return error_response(ErrorCode.JOB_NOT_FOUND, "Job not found.", status.HTTP_404_NOT_FOUND)

    qs = (
        Job.objects
        .filter(status=Job.Status.ACTIVE)
        .exclude(id=job.id)
        .filter(
            Q(job_type=job.job_type) |
            Q(experience_level=job.experience_level) |
            Q(location__icontains=job.location.split(',')[0])
        )
        .select_related('company')
        .distinct()
        [:5]
    )
    serializer = JobMiniSerializer(qs, many=True)
    return Response(serializer.data)


# ─────────────────────────────────────────────────────────────────
# Recruiter — CRUD + Dashboard
# ─────────────────────────────────────────────────────────────────

class JobCreateAPIView(generics.CreateAPIView):
    serializer_class = JobWriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            if request.user.role != User.Role.RECRUITER:
                return error_response(
                    ErrorCode.PERMISSION_DENIED,
                    "Only recruiters can post jobs.",
                    status.HTTP_403_FORBIDDEN,
                )
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            job = serializer.save()

            # Notify followers of the company
            from apps.companies.models import CompanyFollow
            from apps.notifications.services import notify
            from apps.notifications.models import Notification

            followers = CompanyFollow.objects.filter(company=job.company).select_related('candidate')
            for follow in followers:
                notify(
                    recipient=follow.candidate,
                    notification_type=Notification.Type.COMPANY_NEW_JOB,
                    title=f"New job at {job.company.name}",
                    message=f"'{job.title}' has just been posted — check it out!",
                    link=f"/api/v1/jobs/{job.id}/",
                )

            return Response(JobSerializer(job).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return error_response(ErrorCode.JOB_CREATE_FAILED, str(e))


class JobUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobWriteSerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiterOwner]
    queryset = Job.objects.select_related('company').all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        try:
            kwargs['partial'] = True
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return error_response(ErrorCode.JOB_UPDATE_FAILED, str(e))

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return error_response(ErrorCode.JOB_DELETE_FAILED, str(e))


class RecruiterMyJobsView(generics.ListAPIView):
    """Recruiter: list all their posted jobs with analytics."""
    serializer_class = JobMiniSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['created_at', 'view_count', 'application_count', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.role != User.Role.RECRUITER:
            return Job.objects.none()
        return (
            Job.objects
            .filter(company__recruiter=self.request.user)
            .select_related('company')
        )